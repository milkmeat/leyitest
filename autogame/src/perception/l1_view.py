"""L1 局部视图构建 — 将 SyncSnapshot 转化为小队级战术视图

将全局数据过滤为单小队视角：
- 本队成员状态摘要
- 按距离排序的附近敌人 (top 20)
- 按距离排序的附近建筑 (top 15)

用法:
    builder = L1ViewBuilder(config)
    view = builder.build(snapshot, squad, l2_order="进攻东部据点")
    text = builder.format_text(view)  # → LLM user prompt
"""

from __future__ import annotations

import logging
import math
import re

from pydantic import BaseModel, Field

from src.config.schemas import AppConfig, SquadEntry
from src.models.player_state import PlayerState, TroopState
from src.models.building import Building
from src.models.enemy import Enemy
from src.models.rally import RallyBrief
from src.perception.data_sync import SyncSnapshot

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# 视图数据模型
# ------------------------------------------------------------------

class TroopView(BaseModel):
    """部队摘要"""
    unique_id: str = ""
    state: str = "IDLE"          # TroopState 名称
    soldier_count: int = 0
    pos: tuple[int, int] = (0, 0)
    target: str = ""             # 目标描述


class MemberView(BaseModel):
    """小队成员摘要"""
    uid: int
    name: str = ""
    city_pos: tuple[int, int] = (0, 0)
    power: int = 0
    total_soldiers: int = 0
    troops: list[TroopView] = Field(default_factory=list)
    dispatch_slots: int = 0      # 可用出征槽位（最多2）
    queue_status: dict[str, int] = Field(default_factory=dict)  # {"6001":0/1, ...} 0=free, 1=occupied


class NearbyEnemy(BaseModel):
    """附近敌人"""
    uid: int
    name: str = ""
    pos: tuple[int, int] = (0, 0)
    power: int = 0
    alliance: str = ""
    distance: float = 0.0       # 到小队中心的格数
    march_seconds: int = 0      # 行军秒数
    is_fighting: bool = False


class NearbyBuilding(BaseModel):
    """附近建筑"""
    unique_id: str
    obj_type: int = 0
    pos: tuple[int, int] = (0, 0)
    owner_alliance: str = ""     # "中立" / 联盟名
    distance: float = 0.0
    march_seconds: int = 0
    is_fighting: bool = False
    status: int = 0


class ActiveRally(BaseModel):
    """当前活跃集结 — 可加入的集结信息"""
    rally_id: str               # 集结 unique_id（JOIN_RALLY 必填）
    leader_uid: int = 0         # 发起者 UID
    target_id: str = ""         # 目标 unique_id
    target_pos: tuple[int, int] = (0, 0)
    pos: tuple[int, int] = (0, 0)
    status: str = ""            # "gathering" / "marching" / "fighting"


class L1SquadView(BaseModel):
    """L1 小队完整视图 — LLM 输入的结构化数据"""
    squad_id: int
    squad_name: str = ""
    center_pos: tuple[int, int] = (0, 0)
    members: list[MemberView] = Field(default_factory=list)
    enemies: list[NearbyEnemy] = Field(default_factory=list)
    buildings: list[NearbyBuilding] = Field(default_factory=list)
    rallies: list[ActiveRally] = Field(default_factory=list)
    l2_order: str = ""           # L2 战略指令


# ------------------------------------------------------------------
# 视图构建器
# ------------------------------------------------------------------

def _distance(a: tuple[int, int], b: tuple[int, int]) -> float:
    """两点间欧几里得距离"""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


class L1ViewBuilder:
    """从 SyncSnapshot 构建 L1 局部视图"""

    MAX_ENEMIES = 10
    MAX_ENEMIES_DISTANCE = 100  # 超过此距离的敌人不传给 LLM
    MAX_BUILDINGS = 10

    def __init__(self, config: AppConfig):
        self.config = config
        self.march_speed = config.activity.march.speed  # 秒/格
        # AVA 战场用 lvl_aid (1/2) 判断建筑归属；主世界用完整 aid
        alliances = config.accounts.alliances
        if alliances and alliances.ours.lvl_aid:
            self._my_alliance_id = alliances.ours.lvl_aid
        elif alliances:
            self._my_alliance_id = alliances.ours.aid
        else:
            self._my_alliance_id = 0

    def build(
        self,
        snapshot: SyncSnapshot,
        squad: SquadEntry,
        l2_order: str = "",
    ) -> L1SquadView:
        """构建单小队视图

        Args:
            snapshot: 当轮同步快照
            squad: 小队配置
            l2_order: L2 战略指令文本

        Returns:
            L1SquadView 结构化视图
        """
        # 1. 提取本队成员
        members = []
        center_x, center_y = 0, 0
        member_count = 0

        for uid in squad.member_uids:
            acct = snapshot.accounts.get(uid)
            if acct is None:
                continue
            mv = self._build_member_view(acct)
            members.append(mv)
            center_x += acct.city_pos[0]
            center_y += acct.city_pos[1]
            member_count += 1

        # 2. 计算小队几何中心
        if member_count > 0:
            center = (center_x // member_count, center_y // member_count)
        else:
            center = (500, 500)

        # 3. 附近敌人（按距离排序，截取 top N）
        enemies = self._build_nearby_enemies(snapshot.enemies, center)

        # 4. 附近建筑（按距离排序，截取 top N）
        buildings = self._build_nearby_buildings(snapshot.buildings, center)

        # 5. 当前活跃集结（我方发起的、可加入的）
        rallies = self._build_active_rallies(snapshot.rallies)

        return L1SquadView(
            squad_id=squad.squad_id,
            squad_name=squad.name,
            center_pos=center,
            members=members,
            enemies=enemies,
            buildings=buildings,
            rallies=rallies,
            l2_order=l2_order,
        )

    def format_text(self, view: L1SquadView) -> str:
        """Format view as LLM user prompt (structured markdown)"""
        lines: list[str] = []

        lines.append(f"# Squad {view.squad_id} ({view.squad_name}) Status Report")
        lines.append(f"Squad Center: ({view.center_pos[0]}, {view.center_pos[1]})")
        lines.append("")

        # L2 Order
        if view.l2_order:
            lines.append("## L2 Strategic Order")
            lines.append(view.l2_order)
            lines.append("")

        # Friendly members
        lines.append(f"## Friendly Members ({len(view.members)} total)")
        for m in view.members:
            power_str = f" power={m.power}" if m.power else ""
            lines.append(
                f"- uid={m.uid} "
                f"city({m.city_pos[0]},{m.city_pos[1]}){power_str} "
                f"soldiers={m.total_soldiers} "
                f"queues={{{','.join(f'{k}:{v}' for k,v in m.queue_status.items())}}}"
            )
            for t in m.troops:
                if t.state == "IDLE":
                    continue
                lines.append(
                    f"  - {t.state} count={t.soldier_count} "
                    f"pos({t.pos[0]},{t.pos[1]}) target={t.target}"
                )
        lines.append("")

        # Nearby enemies
        lines.append(f"## Nearby Enemies ({len(view.enemies)} total)")
        if view.enemies:
            for e in view.enemies:
                fight = " [FIGHTING]" if e.is_fighting else ""
                power_str = f" power={e.power}" if e.power else ""
                lines.append(
                    f"- uid={e.uid} ({e.pos[0]},{e.pos[1]}){power_str} "
                    f"alliance={e.alliance} "
                    f"dist={e.distance:.0f} march≈{e.march_seconds}s{fight}"
                )
        else:
            lines.append("- (none)")
        lines.append("")

        # Nearby buildings
        lines.append(f"## Nearby Buildings ({len(view.buildings)} total)")
        if view.buildings:
            for b in view.buildings:
                fight = " [FIGHTING]" if b.is_fighting else ""
                lines.append(
                    f"- {b.unique_id} type={b.obj_type} "
                    f"({b.pos[0]},{b.pos[1]}) "
                    f"owner={b.owner_alliance} "
                    f"dist={b.distance:.0f} march≈{b.march_seconds}s{fight}"
                )
        else:
            lines.append("- (none)")

        # Active rallies (joinable)
        if view.rallies:
            lines.append("")
            lines.append(f"## Active Rallies ({len(view.rallies)} joinable)")
            for r in view.rallies:
                lines.append(
                    f"- rally_id={r.rally_id} leader_uid={r.leader_uid} "
                    f"target={r.target_id} target_pos({r.target_pos[0]},{r.target_pos[1]}) "
                    f"pos({r.pos[0]},{r.pos[1]}) status={r.status}"
                )

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    @staticmethod
    def _build_member_view(acct: PlayerState) -> MemberView:
        """从 PlayerState 构建成员摘要"""
        troops = []

        for t in acct.troops:
            soldier_count = sum(t.soldiers.values()) if t.soldiers else 0
            tv = TroopView(
                unique_id=t.unique_id,
                state=TroopState(t.state).name,
                soldier_count=soldier_count,
                pos=t.pos,
                target=t.target_unique_id,
            )
            troops.append(tv)

        # 按 queue_id 检测占用状态
        queue_status = {"6001": 0, "6002": 0, "6003": 0, "6004": 0}
        for t in acct.troops:
            if t.state != TroopState.IDLE and t.queue_id > 0:
                qkey = str(t.queue_id)
                if qkey in queue_status:
                    queue_status[qkey] = 1
        dispatch_slots = sum(1 for v in queue_status.values() if v == 0)

        total_soldiers = sum(s.value for s in acct.soldiers)

        return MemberView(
            uid=acct.uid,
            name=acct.name,
            city_pos=acct.city_pos,
            power=acct.power,
            total_soldiers=total_soldiers,
            troops=troops,
            dispatch_slots=dispatch_slots,
            queue_status=queue_status,
        )

    def _build_nearby_enemies(
        self,
        enemies: list[Enemy],
        center: tuple[int, int],
    ) -> list[NearbyEnemy]:
        """按距离排序，截取 top N 敌人"""
        items = []
        for e in enemies:
            dist = _distance(center, e.city_pos)
            march_sec = int(dist * self.march_speed)
            items.append(NearbyEnemy(
                uid=e.uid,
                name=e.name,
                pos=e.city_pos,
                power=e.power,
                alliance=e.alliance_name or f"aid={e.alliance_id}",
                distance=round(dist, 1),
                march_seconds=march_sec,
                is_fighting=e.is_fighting,
            ))
        items.sort(key=lambda x: x.distance)
        items = [e for e in items if e.distance <= self.MAX_ENEMIES_DISTANCE]
        return items[:self.MAX_ENEMIES]

    def _build_nearby_buildings(
        self,
        buildings: list[Building],
        center: tuple[int, int],
    ) -> list[NearbyBuilding]:
        """Sort by distance, take top N buildings"""
        items = []
        for b in buildings:
            dist = _distance(center, b.pos)
            march_sec = int(dist * self.march_speed)
            if b.alliance_id == 0:
                owner = "Neutral"
            elif self._my_alliance_id and b.alliance_id == self._my_alliance_id:
                owner = "Ours"
            elif b.alliance_id != 0:
                owner = "Enemy"
            elif b.alliance_nick:
                owner = b.alliance_nick
            elif b.alliance_name:
                owner = b.alliance_name
            else:
                owner = f"aid={b.alliance_id}"
            items.append(NearbyBuilding(
                unique_id=b.unique_id,
                obj_type=b.obj_type,
                pos=b.pos,
                owner_alliance=owner,
                distance=round(dist, 1),
                march_seconds=march_sec,
                is_fighting=b.is_fighting,
                status=b.status,
            ))
        items.sort(key=lambda x: x.distance)
        return items[:self.MAX_BUILDINGS]

    @staticmethod
    def _build_active_rallies(
        rallies: list[RallyBrief],
    ) -> list[ActiveRally]:
        """构建当前活跃集结列表（可加入的集结）"""
        _STATUS_MAP = {0: "gathering", 1: "marching", 6: "gathering"}
        items = []
        for r in rallies:
            # status=6 表示集合中（可加入），status=0 也可能是等待中
            # status=1 表示行军中（不可加入但有参考价值）
            status_str = _STATUS_MAP.get(r.status, f"status_{r.status}")
            items.append(ActiveRally(
                rally_id=r.unique_id,
                leader_uid=r.leader_uid,
                target_id=r.target_id,
                target_pos=r.target_pos,
                pos=r.pos,
                status=status_str,
            ))
        return items


# ------------------------------------------------------------------
# 工具函数：坐标解析与建筑处理
# ------------------------------------------------------------------

def parse_target_coordinates(l2_order: str) -> tuple[int, int] | None:
    """从 L2 指令中解析目标坐标

    支持的格式:
    - "控制 建筑 pos:( 154, 170 )" -> (154, 170)
    - "move to (100, 200)" -> (100, 200)
    - "attack 100,200" -> (100, 200)

    Returns:
        (x, y) 元组，解析失败时返回 None
    """
    # 尝试匹配 "pos:( x, y )" 格式
    pattern = r'pos:\(\s*(\d+)\s*,\s*(\d+)\s*\)'
    match = re.search(pattern, l2_order)
    if match:
        return (int(match.group(1)), int(match.group(2)))

    # 尝试匹配 "(x, y)" 格式
    pattern = r'\(\s*(\d+)\s*,\s*(\d+)\s*\)'
    match = re.search(pattern, l2_order)
    if match:
        return (int(match.group(1)), int(match.group(2)))

    # 尝试匹配 "x, y" 格式
    pattern = r'(\d{1,3})\s*,\s*(\d{1,3})'
    match = re.search(pattern, l2_order)
    if match:
        x, y = int(match.group(1)), int(match.group(2))
        if 0 <= x < 1000 and 0 <= y < 1000:
            return (x, y)

    return None


def find_building_by_pos(
    buildings: list[Building],
    target_pos: tuple[int, int],
    tolerance: int = 2,
) -> Building | None:
    """在建筑列表中查找指定坐标附近的建筑

    Args:
        buildings: 建筑列表
        target_pos: 目标坐标
        tolerance: 坐标容差（格数），默认 2 格

    Returns:
        找到的建筑，未找到时返回 None
    """
    target_x, target_y = target_pos

    for b in buildings:
        if abs(b.pos[0] - target_x) <= tolerance and abs(b.pos[1] - target_y) <= tolerance:
            return b

    return None


def get_building_control_status(building: Building, my_alliance_id: int) -> str:
    """获取建筑控制状态描述

    Returns:
        "中立" / "我方" / "敌方"
    """
    if building.alliance_id == 0:
        return "中立"
    elif building.alliance_id == my_alliance_id:
        return "我方"
    else:
        return "敌方"
