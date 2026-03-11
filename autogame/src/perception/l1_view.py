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

import math

from pydantic import BaseModel, Field

from src.config.schemas import AppConfig, SquadEntry
from src.models.account import Account, TroopState
from src.models.building import Building
from src.models.enemy import Enemy
from src.perception.data_sync import SyncSnapshot


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
    idle_troop_count: int = 0    # 空闲部队数


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


class L1SquadView(BaseModel):
    """L1 小队完整视图 — LLM 输入的结构化数据"""
    squad_id: int
    squad_name: str = ""
    center_pos: tuple[int, int] = (0, 0)
    members: list[MemberView] = Field(default_factory=list)
    enemies: list[NearbyEnemy] = Field(default_factory=list)
    buildings: list[NearbyBuilding] = Field(default_factory=list)
    l2_order: str = ""           # L2 战略指令


# ------------------------------------------------------------------
# 视图构建器
# ------------------------------------------------------------------

def _distance(a: tuple[int, int], b: tuple[int, int]) -> float:
    """两点间欧几里得距离"""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


class L1ViewBuilder:
    """从 SyncSnapshot 构建 L1 局部视图"""

    MAX_ENEMIES = 20
    MAX_BUILDINGS = 15

    def __init__(self, config: AppConfig):
        self.config = config
        self.march_speed = config.activity.march.speed  # 秒/格

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

        return L1SquadView(
            squad_id=squad.squad_id,
            squad_name=squad.name,
            center_pos=center,
            members=members,
            enemies=enemies,
            buildings=buildings,
            l2_order=l2_order,
        )

    def format_text(self, view: L1SquadView) -> str:
        """将视图格式化为 LLM user prompt (结构化 markdown)"""
        lines: list[str] = []

        lines.append(f"# 小队 {view.squad_id} ({view.squad_name}) 态势报告")
        lines.append(f"小队中心: ({view.center_pos[0]}, {view.center_pos[1]})")
        lines.append("")

        # L2 指令
        if view.l2_order:
            lines.append("## L2 战略指令")
            lines.append(view.l2_order)
            lines.append("")

        # 友方成员
        lines.append(f"## 友方成员 ({len(view.members)} 人)")
        for m in view.members:
            lines.append(
                f"- uid={m.uid} {m.name} "
                f"城({m.city_pos[0]},{m.city_pos[1]}) "
                f"战力={m.power} 兵力={m.total_soldiers} "
                f"空闲部队={m.idle_troop_count}"
            )
            for t in m.troops:
                lines.append(
                    f"  - 部队 {t.unique_id}: {t.state} "
                    f"兵={t.soldier_count} 位置({t.pos[0]},{t.pos[1]}) "
                    f"{t.target}"
                )
        lines.append("")

        # 附近敌方
        lines.append(f"## 附近敌方 ({len(view.enemies)} 个)")
        if view.enemies:
            for e in view.enemies:
                fight = " [战斗中]" if e.is_fighting else ""
                lines.append(
                    f"- uid={e.uid} ({e.pos[0]},{e.pos[1]}) "
                    f"战力={e.power} 联盟={e.alliance} "
                    f"距离={e.distance:.0f}格 行军≈{e.march_seconds}s{fight}"
                )
        else:
            lines.append("- (无)")
        lines.append("")

        # 附近建筑
        lines.append(f"## 附近建筑 ({len(view.buildings)} 个)")
        if view.buildings:
            for b in view.buildings:
                fight = " [战斗中]" if b.is_fighting else ""
                lines.append(
                    f"- {b.unique_id} type={b.obj_type} "
                    f"({b.pos[0]},{b.pos[1]}) "
                    f"归属={b.owner_alliance} "
                    f"距离={b.distance:.0f}格 行军≈{b.march_seconds}s{fight}"
                )
        else:
            lines.append("- (无)")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    @staticmethod
    def _build_member_view(acct: Account) -> MemberView:
        """从 Account 构建成员摘要"""
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

        # 账号有 3 个部队槽位，在外部队之外的都算空闲
        busy_count = len([t for t in acct.troops if t.state != TroopState.IDLE])
        idle_count = max(0, 3 - busy_count)

        total_soldiers = sum(s.value for s in acct.soldiers)

        return MemberView(
            uid=acct.uid,
            name=acct.name,
            city_pos=acct.city_pos,
            power=acct.power,
            total_soldiers=total_soldiers,
            troops=troops,
            idle_troop_count=idle_count,
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
        return items[:self.MAX_ENEMIES]

    def _build_nearby_buildings(
        self,
        buildings: list[Building],
        center: tuple[int, int],
    ) -> list[NearbyBuilding]:
        """按距离排序，截取 top N 建筑"""
        items = []
        for b in buildings:
            dist = _distance(center, b.pos)
            march_sec = int(dist * self.march_speed)
            if b.alliance_id == 0:
                owner = "中立"
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
