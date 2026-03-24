"""L2 全局视图构建 — 将 SyncSnapshot 转化为军团级战略视图

将全局数据聚合为 L2 指挥官视角：
- 小队级兵力摘要（不暴露单个账号细节）
- DBSCAN 聚类敌方玩家为威胁集群
- 建筑控制态势总览
- 全军战力对比

用法:
    builder = L2ViewBuilder(config)
    view = builder.build(snapshot)
    text = builder.format_text(view)  # → L2 LLM user prompt
"""

from __future__ import annotations

import logging
import math

import numpy as np
from pydantic import BaseModel, Field
from sklearn.cluster import DBSCAN

from src.config.schemas import AppConfig
from src.models.building import Building
from src.models.enemy import Enemy
from src.models.player_state import PlayerState, TroopState
from src.perception.data_sync import SyncSnapshot

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# 视图数据模型
# ------------------------------------------------------------------

class SquadSummary(BaseModel):
    """小队摘要 — L2 视角下的单小队状态"""
    squad_id: int
    name: str = ""
    member_count: int = 0              # 成功同步的成员数
    total_power: int = 0               # 小队总战力
    total_soldiers: int = 0            # 小队总兵力
    center_pos: tuple[int, int] = (0, 0)  # 几何中心
    available_slots: int = 0           # 可用出征槽位总数 (max 2*N)
    busy_troops: int = 0              # 在外部队数
    is_under_attack: bool = False      # 是否有成员正在被攻击


class EnemyCluster(BaseModel):
    """敌方聚类 — DBSCAN 聚合后的威胁群"""
    cluster_id: int
    center_pos: tuple[int, int] = (0, 0)
    enemy_count: int = 0
    total_power: int = 0
    bbox: tuple[int, int, int, int] = (0, 0, 0, 0)  # (min_x, min_y, max_x, max_y)
    nearest_squad_id: int = 0
    nearest_distance: float = 0.0      # 到最近小队的格数
    fighting_count: int = 0            # 战斗中的敌人数


class BuildingSummary(BaseModel):
    """建筑态势摘要"""
    total: int = 0
    ally_held: int = 0
    enemy_held: int = 0
    neutral: int = 0
    contested: int = 0                 # 战斗中


class BuildingDetail(BaseModel):
    """单个关键建筑详情"""
    unique_id: str
    obj_type: int = 0
    pos: tuple[int, int] = (0, 0)
    owner_side: str = "neutral"        # "neutral" / "ally" / "enemy"
    is_fighting: bool = False


class L2GlobalView(BaseModel):
    """L2 全局视图 — L2 LLM 的结构化输入"""
    loop_id: int = 0
    squads: list[SquadSummary] = Field(default_factory=list)
    enemy_clusters: list[EnemyCluster] = Field(default_factory=list)
    scattered_enemies: int = 0         # 未归入集群的散兵数
    buildings: BuildingSummary = Field(default_factory=BuildingSummary)
    building_details: list[BuildingDetail] = Field(default_factory=list)
    army_center: tuple[int, int] = (0, 0)   # 全军几何中心
    total_power: int = 0               # 我方总战力
    total_soldiers: int = 0            # 我方总兵力
    total_enemy_power: int = 0         # 可见敌方总战力


# ------------------------------------------------------------------
# 辅助函数
# ------------------------------------------------------------------

def _distance(a: tuple[int, int], b: tuple[int, int]) -> float:
    """两点间欧几里得距离"""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


# ------------------------------------------------------------------
# 视图构建器
# ------------------------------------------------------------------

class L2ViewBuilder:
    """从 SyncSnapshot 构建 L2 全局视图"""

    # DBSCAN 参数
    DBSCAN_EPS = 150          # 150 格内视为同一集群
    DBSCAN_MIN_SAMPLES = 2    # 最少 2 人才成集群

    # 建筑详情最大数量
    MAX_BUILDING_DETAILS = 20

    def __init__(self, config: AppConfig):
        self.config = config
        self.march_speed = config.activity.march.speed  # 秒/格
        self._my_alliance_id = 0
        alliances = config.accounts.alliances
        if alliances:
            # AVA 战场用 lvl_aid (1/2)；主世界用完整 aid
            self._my_alliance_id = alliances.ours.lvl_aid or alliances.ours.aid

    def build(self, snapshot: SyncSnapshot) -> L2GlobalView:
        """构建全局视图

        Args:
            snapshot: 当轮同步快照

        Returns:
            L2GlobalView 结构化视图
        """
        # 1. 按小队聚合账号
        squads = self._build_squad_summaries(snapshot)

        # 2. DBSCAN 聚类敌方玩家
        enemy_clusters, scattered = self._cluster_enemies(
            snapshot.enemies, squads
        )

        # 3. 建筑态势
        building_summary, building_details = self._build_building_info(
            snapshot.buildings
        )

        # 4. 全军聚合指标
        total_power = sum(s.total_power for s in squads)
        total_soldiers = sum(s.total_soldiers for s in squads)
        total_enemy_power = sum(e.power for e in snapshot.enemies)
        army_center = self._compute_army_center(squads)

        return L2GlobalView(
            loop_id=snapshot.loop_id,
            squads=squads,
            enemy_clusters=enemy_clusters,
            scattered_enemies=scattered,
            buildings=building_summary,
            building_details=building_details,
            army_center=army_center,
            total_power=total_power,
            total_soldiers=total_soldiers,
            total_enemy_power=total_enemy_power,
        )

    def format_text(self, view: L2GlobalView) -> str:
        """将视图格式化为 markdown 供 L2 LLM 阅读"""
        lines: list[str] = []

        # 标题
        lines.append(f"# 全局战情摘要 (Loop #{view.loop_id})")
        lines.append("")

        # 总体态势
        lines.append("## 总体态势")
        lines.append(
            f"- 我方总战力: {view.total_power:,} | "
            f"总兵力: {view.total_soldiers:,}"
        )
        lines.append(f"- 敌方可见总战力: {view.total_enemy_power:,}")
        lines.append(
            f"- 全军中心: ({view.army_center[0]}, {view.army_center[1]})"
        )
        b = view.buildings
        lines.append(
            f"- 建筑: 共{b.total} | "
            f"我方{b.ally_held} 敌方{b.enemy_held} "
            f"中立{b.neutral} 交战{b.contested}"
        )
        lines.append("")

        # 小队状态
        lines.append(f"## 小队状态 ({len(view.squads)}个)")
        lines.append(
            "| 小队 | 人数 | 战力 | 兵力 | 中心 | 空闲槽 | 在外部队 | 受攻击 |"
        )
        lines.append(
            "|------|------|------|------|------|--------|----------|--------|"
        )
        for s in view.squads:
            attack_flag = "是" if s.is_under_attack else ""
            lines.append(
                f"| {s.squad_id}-{s.name} "
                f"| {s.member_count} "
                f"| {s.total_power:,} "
                f"| {s.total_soldiers:,} "
                f"| ({s.center_pos[0]},{s.center_pos[1]}) "
                f"| {s.available_slots} "
                f"| {s.busy_troops} "
                f"| {attack_flag} |"
            )
        lines.append("")

        # 敌方威胁集群
        cluster_count = len(view.enemy_clusters)
        lines.append(
            f"## 敌方威胁集群 ({cluster_count}个"
            f", 散兵{view.scattered_enemies}人)"
        )
        if view.enemy_clusters:
            for c in view.enemy_clusters:
                fight_info = (
                    f" [{c.fighting_count}人战斗中]"
                    if c.fighting_count else ""
                )
                lines.append(
                    f"- 集群{c.cluster_id}: {c.enemy_count}人 "
                    f"战力{c.total_power:,} "
                    f"区域({c.bbox[0]}-{c.bbox[2]}, "
                    f"{c.bbox[1]}-{c.bbox[3]}) "
                    f"最近→{c.nearest_squad_id}号队"
                    f"({c.nearest_distance:.0f}格)"
                    f"{fight_info}"
                )
        else:
            lines.append("- (未发现集群)")
        lines.append("")

        # 关键建筑
        lines.append(f"## 关键建筑 ({len(view.building_details)}个)")
        if view.building_details:
            for bd in view.building_details:
                fight = " [交战中]" if bd.is_fighting else ""
                side_label = {
                    "ally": "我方",
                    "enemy": "敌方",
                    "neutral": "中立",
                }.get(bd.owner_side, bd.owner_side)
                lines.append(
                    f"- {bd.unique_id} type={bd.obj_type} "
                    f"({bd.pos[0]},{bd.pos[1]}) "
                    f"{side_label}{fight}"
                )
        else:
            lines.append("- (无)")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _build_squad_summaries(
        self, snapshot: SyncSnapshot,
    ) -> list[SquadSummary]:
        """按小队聚合成员数据"""
        summaries: list[SquadSummary] = []

        for squad in self.config.squads.squads:
            cx, cy = 0, 0
            count = 0
            total_power = 0
            total_soldiers = 0
            available_slots = 0
            busy_troops = 0
            under_attack = False

            for uid in squad.member_uids:
                acct = snapshot.accounts.get(uid)
                if acct is None:
                    continue
                count += 1
                cx += acct.city_pos[0]
                cy += acct.city_pos[1]
                total_power += acct.power
                total_soldiers += sum(s.value for s in acct.soldiers)

                # 统计出征槽位
                busy = len([
                    t for t in acct.troops
                    if t.state != TroopState.IDLE
                ])
                busy_troops += busy
                available_slots += max(0, 2 - busy)

                # 检查是否被攻击（有处于 FIGHTING 状态的部队）
                if any(t.state == TroopState.FIGHTING for t in acct.troops):
                    under_attack = True

            center = (cx // count, cy // count) if count > 0 else (500, 500)

            summaries.append(SquadSummary(
                squad_id=squad.squad_id,
                name=squad.name,
                member_count=count,
                total_power=total_power,
                total_soldiers=total_soldiers,
                center_pos=center,
                available_slots=available_slots,
                busy_troops=busy_troops,
                is_under_attack=under_attack,
            ))

        return summaries

    def _cluster_enemies(
        self,
        enemies: list[Enemy],
        squads: list[SquadSummary],
    ) -> tuple[list[EnemyCluster], int]:
        """DBSCAN 聚类敌方玩家

        Returns:
            (聚类列表, 散兵数量)
        """
        if len(enemies) < self.DBSCAN_MIN_SAMPLES:
            # 敌人太少，全部视为散兵
            return [], len(enemies)

        # 构建坐标矩阵
        coords = np.array(
            [[e.city_pos[0], e.city_pos[1]] for e in enemies],
            dtype=np.float64,
        )

        # 运行 DBSCAN
        db = DBSCAN(
            eps=self.DBSCAN_EPS,
            min_samples=self.DBSCAN_MIN_SAMPLES,
            metric="euclidean",
        )
        labels = db.fit_predict(coords)

        # 按标签分组
        clusters: dict[int, list[int]] = {}  # label → [index]
        scattered_count = 0
        for idx, label in enumerate(labels):
            if label == -1:
                scattered_count += 1
            else:
                clusters.setdefault(label, []).append(idx)

        # 构建 EnemyCluster
        result: list[EnemyCluster] = []
        for cluster_id, (label, indices) in enumerate(
            sorted(clusters.items())
        ):
            cluster_enemies = [enemies[i] for i in indices]
            cluster_coords = coords[indices]

            # 中心
            cx = int(cluster_coords[:, 0].mean())
            cy = int(cluster_coords[:, 1].mean())
            center = (cx, cy)

            # 边界框
            min_x = int(cluster_coords[:, 0].min())
            min_y = int(cluster_coords[:, 1].min())
            max_x = int(cluster_coords[:, 0].max())
            max_y = int(cluster_coords[:, 1].max())

            # 总战力 & 战斗中数量
            total_power = sum(e.power for e in cluster_enemies)
            fighting = sum(1 for e in cluster_enemies if e.is_fighting)

            # 找最近的小队
            nearest_sid = 0
            nearest_dist = float("inf")
            for s in squads:
                d = _distance(center, s.center_pos)
                if d < nearest_dist:
                    nearest_dist = d
                    nearest_sid = s.squad_id

            result.append(EnemyCluster(
                cluster_id=cluster_id,
                center_pos=center,
                enemy_count=len(cluster_enemies),
                total_power=total_power,
                bbox=(min_x, min_y, max_x, max_y),
                nearest_squad_id=nearest_sid,
                nearest_distance=round(nearest_dist, 1),
                fighting_count=fighting,
            ))

        # 按战力降序排列
        result.sort(key=lambda c: c.total_power, reverse=True)

        return result, scattered_count

    def _build_building_info(
        self, buildings: list[Building],
    ) -> tuple[BuildingSummary, list[BuildingDetail]]:
        """统计建筑归属并提取详情"""
        ally = 0
        enemy = 0
        neutral = 0
        contested = 0

        details: list[BuildingDetail] = []

        for b in buildings:
            side = b.owner_side(self._my_alliance_id)
            if side == "ally":
                ally += 1
            elif side == "enemy":
                enemy += 1
            else:
                neutral += 1

            if b.is_fighting:
                contested += 1

            details.append(BuildingDetail(
                unique_id=b.unique_id,
                obj_type=b.obj_type,
                pos=b.pos,
                owner_side=side,
                is_fighting=b.is_fighting,
            ))

        # 排序：交战中优先，然后敌方，然后中立，最后我方
        side_priority = {"enemy": 0, "neutral": 1, "ally": 2}
        details.sort(key=lambda d: (
            not d.is_fighting,
            side_priority.get(d.owner_side, 3),
        ))
        details = details[:self.MAX_BUILDING_DETAILS]

        summary = BuildingSummary(
            total=len(buildings),
            ally_held=ally,
            enemy_held=enemy,
            neutral=neutral,
            contested=contested,
        )
        return summary, details

    @staticmethod
    def _compute_army_center(
        squads: list[SquadSummary],
    ) -> tuple[int, int]:
        """按小队战力加权计算全军中心"""
        total_weight = 0
        wx, wy = 0, 0
        for s in squads:
            if s.member_count == 0:
                continue
            w = s.total_power or 1  # 避免零权重
            wx += s.center_pos[0] * w
            wy += s.center_pos[1] * w
            total_weight += w

        if total_weight == 0:
            return (500, 500)
        return (wx // total_weight, wy // total_weight)
