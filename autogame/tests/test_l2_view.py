"""L2 全局视图单元测试

覆盖:
- 小队聚合 (SquadSummary)
- DBSCAN 敌方聚类 (EnemyCluster + 散兵)
- 建筑态势统计 (BuildingSummary + 排序)
- 全军中心加权计算
- format_text markdown 输出
- 边界情况 (空快照、单个敌人、无建筑)
"""

import pytest

from src.config.schemas import (
    AccountEntry,
    AccountsConfig,
    ActivityConfig,
    AllianceInfo,
    AlliancesConfig,
    AllianceSquadGroup,
    AppConfig,
    SquadEntry,
    SquadsConfig,
    SystemConfig,
)
from src.models.building import Building
from src.models.enemy import Enemy
from src.models.player_state import PlayerState, Soldier, Troop, TroopState
from src.perception.data_sync import SyncSnapshot
from src.perception.l2_view import (
    BuildingDetail,
    BuildingSummary,
    EnemyCluster,
    L2GlobalView,
    L2ViewBuilder,
    SquadSummary,
)


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture()
def config_2squads() -> AppConfig:
    """2 小队、10 账号的最小配置"""
    return AppConfig(
        accounts=AccountsConfig(
            accounts=[AccountEntry(uid=i, name=f"p{i}") for i in range(1, 11)],
            alliances=AlliancesConfig(
                ours=AllianceInfo(aid=100, name="Ours"),
                enemy=AllianceInfo(aid=200, name="Enemy"),
            ),
        ),
        squads=SquadsConfig(alliances={"ours": AllianceSquadGroup(
            aid=100, name="Ours", squads=[
                SquadEntry(squad_id=1, name="Alpha", leader_uid=1, member_uids=[1, 2, 3, 4, 5]),
                SquadEntry(squad_id=2, name="Bravo", leader_uid=6, member_uids=[6, 7, 8, 9, 10]),
            ],
        )}),
        activity=ActivityConfig(),
        system=SystemConfig(),
    )


def _make_account(uid: int, x: int, y: int, power: int = 50000,
                   soldiers: int = 5000, troops: list[Troop] | None = None) -> PlayerState:
    """构造 mock PlayerState"""
    return PlayerState(
        uid=uid,
        name=f"p{uid}",
        city_pos=(x, y),
        power=power,
        soldiers=[Soldier(id=101, value=soldiers)],
        troops=troops or [],
    )


def _make_snapshot(
    accounts: dict[int, PlayerState] | None = None,
    enemies: list[Enemy] | None = None,
    buildings: list[Building] | None = None,
    loop_id: int = 1,
) -> SyncSnapshot:
    return SyncSnapshot(
        accounts=accounts or {},
        enemies=enemies or [],
        buildings=buildings or [],
        loop_id=loop_id,
    )


# ------------------------------------------------------------------
# 小队聚合
# ------------------------------------------------------------------

class TestSquadSummaries:
    def test_basic_aggregation(self, config_2squads: AppConfig):
        """正确聚合小队战力、兵力、中心"""
        accounts = {i: _make_account(i, x=100, y=200, power=10000, soldiers=1000)
                    for i in range(1, 11)}
        snapshot = _make_snapshot(accounts=accounts)
        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)

        assert len(view.squads) == 2
        s1 = view.squads[0]
        assert s1.squad_id == 1
        assert s1.member_count == 5
        assert s1.total_power == 50000
        assert s1.total_soldiers == 5000
        assert s1.available_slots == 10  # 5 成员 × 2 槽位
        assert s1.busy_troops == 0
        assert s1.is_under_attack is False

    def test_busy_troops_reduce_slots(self, config_2squads: AppConfig):
        """在外部队占用出征槽位"""
        troop = Troop(unique_id="108_1_1", state=TroopState.MARCHING)
        accounts = {i: _make_account(i, 100, 200) for i in range(1, 11)}
        accounts[1] = _make_account(1, 100, 200, troops=[troop])
        snapshot = _make_snapshot(accounts=accounts)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        s1 = view.squads[0]
        assert s1.busy_troops == 1
        assert s1.available_slots == 9  # 4×2 + (2-1)

    def test_under_attack_detection(self, config_2squads: AppConfig):
        """检测成员被攻击"""
        troop = Troop(unique_id="108_1_1", state=TroopState.FIGHTING)
        accounts = {i: _make_account(i, 100, 200) for i in range(1, 11)}
        accounts[3] = _make_account(3, 100, 200, troops=[troop])
        snapshot = _make_snapshot(accounts=accounts)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert view.squads[0].is_under_attack is True
        assert view.squads[1].is_under_attack is False

    def test_missing_accounts_handled(self, config_2squads: AppConfig):
        """部分账号同步失败时不崩溃"""
        # 只给 squad 1 的 3 个成员
        accounts = {i: _make_account(i, 100, 200) for i in [1, 2, 3]}
        snapshot = _make_snapshot(accounts=accounts)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert view.squads[0].member_count == 3
        assert view.squads[1].member_count == 0  # 全部缺失
        assert view.squads[1].center_pos == (500, 500)  # 默认值

    def test_center_pos_calculation(self, config_2squads: AppConfig):
        """几何中心正确计算"""
        accounts = {}
        for i, uid in enumerate([1, 2, 3, 4, 5]):
            accounts[uid] = _make_account(uid, x=100 + i * 20, y=200)
        for uid in range(6, 11):
            accounts[uid] = _make_account(uid, x=500, y=500)
        snapshot = _make_snapshot(accounts=accounts)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        # squad 1: x = (100+120+140+160+180)/5 = 140
        assert view.squads[0].center_pos == (140, 200)
        assert view.squads[1].center_pos == (500, 500)


# ------------------------------------------------------------------
# DBSCAN 敌方聚类
# ------------------------------------------------------------------

class TestEnemyClustering:
    def test_nearby_enemies_form_cluster(self, config_2squads: AppConfig):
        """距离 < eps 的敌人归入同一集群"""
        accounts = {i: _make_account(i, 100, 200) for i in range(1, 11)}
        enemies = [
            Enemy(uid=1001, city_pos=(300, 300), power=80000),
            Enemy(uid=1002, city_pos=(310, 310), power=70000),
            Enemy(uid=1003, city_pos=(320, 290), power=60000),
        ]
        snapshot = _make_snapshot(accounts=accounts, enemies=enemies)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert len(view.enemy_clusters) == 1
        assert view.enemy_clusters[0].enemy_count == 3
        assert view.enemy_clusters[0].total_power == 210000
        assert view.scattered_enemies == 0

    def test_distant_enemy_is_scattered(self, config_2squads: AppConfig):
        """远离集群的敌人标记为散兵"""
        accounts = {i: _make_account(i, 100, 200) for i in range(1, 11)}
        enemies = [
            Enemy(uid=1001, city_pos=(300, 300), power=80000),
            Enemy(uid=1002, city_pos=(310, 310), power=70000),
            Enemy(uid=1003, city_pos=(700, 700), power=90000),  # 远离
        ]
        snapshot = _make_snapshot(accounts=accounts, enemies=enemies)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert len(view.enemy_clusters) == 1
        assert view.enemy_clusters[0].enemy_count == 2
        assert view.scattered_enemies == 1

    def test_too_few_enemies_all_scattered(self, config_2squads: AppConfig):
        """敌人数 < min_samples 时全部为散兵"""
        accounts = {i: _make_account(i, 100, 200) for i in range(1, 11)}
        enemies = [Enemy(uid=1001, city_pos=(300, 300), power=50000)]
        snapshot = _make_snapshot(accounts=accounts, enemies=enemies)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert len(view.enemy_clusters) == 0
        assert view.scattered_enemies == 1

    def test_no_enemies(self, config_2squads: AppConfig):
        """无敌人时集群和散兵都为空"""
        accounts = {i: _make_account(i, 100, 200) for i in range(1, 11)}
        snapshot = _make_snapshot(accounts=accounts)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert len(view.enemy_clusters) == 0
        assert view.scattered_enemies == 0

    def test_multiple_clusters(self, config_2squads: AppConfig):
        """形成多个不同集群"""
        accounts = {i: _make_account(i, 100, 200) for i in range(1, 11)}
        enemies = [
            # 集群 A: 左上
            Enemy(uid=1001, city_pos=(100, 100), power=50000),
            Enemy(uid=1002, city_pos=(120, 110), power=40000),
            # 集群 B: 右下（距离 > 150 格）
            Enemy(uid=1003, city_pos=(800, 800), power=70000),
            Enemy(uid=1004, city_pos=(810, 790), power=60000),
        ]
        snapshot = _make_snapshot(accounts=accounts, enemies=enemies)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert len(view.enemy_clusters) == 2
        assert view.scattered_enemies == 0
        # 按战力降序排列
        assert view.enemy_clusters[0].total_power >= view.enemy_clusters[1].total_power

    def test_cluster_bbox(self, config_2squads: AppConfig):
        """集群边界框正确"""
        accounts = {i: _make_account(i, 100, 200) for i in range(1, 11)}
        enemies = [
            Enemy(uid=1001, city_pos=(300, 400), power=50000),
            Enemy(uid=1002, city_pos=(350, 350), power=50000),
        ]
        snapshot = _make_snapshot(accounts=accounts, enemies=enemies)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        c = view.enemy_clusters[0]
        assert c.bbox == (300, 350, 350, 400)

    def test_cluster_nearest_squad(self, config_2squads: AppConfig):
        """集群找到最近的小队"""
        accounts = {}
        for uid in range(1, 6):
            accounts[uid] = _make_account(uid, x=100, y=100)  # squad 1 在左上
        for uid in range(6, 11):
            accounts[uid] = _make_account(uid, x=800, y=800)  # squad 2 在右下
        enemies = [
            Enemy(uid=1001, city_pos=(750, 750), power=50000),
            Enemy(uid=1002, city_pos=(760, 760), power=50000),
        ]
        snapshot = _make_snapshot(accounts=accounts, enemies=enemies)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert view.enemy_clusters[0].nearest_squad_id == 2

    def test_fighting_count(self, config_2squads: AppConfig):
        """统计集群中战斗中的敌人数"""
        accounts = {i: _make_account(i, 100, 200) for i in range(1, 11)}
        enemies = [
            Enemy(uid=1001, city_pos=(300, 300), power=50000, fight_flag=1),
            Enemy(uid=1002, city_pos=(310, 310), power=50000, fight_flag=0),
            Enemy(uid=1003, city_pos=(320, 300), power=50000, fight_flag=1),
        ]
        snapshot = _make_snapshot(accounts=accounts, enemies=enemies)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert view.enemy_clusters[0].fighting_count == 2


# ------------------------------------------------------------------
# 建筑态势
# ------------------------------------------------------------------

class TestBuildingInfo:
    def test_owner_classification(self, config_2squads: AppConfig):
        """按联盟 ID 正确分类建筑归属"""
        accounts = {i: _make_account(i, 100, 200) for i in range(1, 11)}
        buildings = [
            Building(unique_id="b1", obj_type=27, alliance_id=0),      # 中立
            Building(unique_id="b2", obj_type=27, alliance_id=100),    # 我方
            Building(unique_id="b3", obj_type=27, alliance_id=200),    # 敌方
            Building(unique_id="b4", obj_type=48, alliance_id=200, fight_flag=1),  # 敌方+交战
        ]
        snapshot = _make_snapshot(accounts=accounts, buildings=buildings)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert view.buildings.total == 4
        assert view.buildings.ally_held == 1
        assert view.buildings.enemy_held == 2
        assert view.buildings.neutral == 1
        assert view.buildings.contested == 1

    def test_building_details_sorted(self, config_2squads: AppConfig):
        """建筑详情排序: 交战中 > 敌方 > 中立 > 我方"""
        accounts = {i: _make_account(i, 100, 200) for i in range(1, 11)}
        buildings = [
            Building(unique_id="ally1", obj_type=27, alliance_id=100),
            Building(unique_id="neutral1", obj_type=27, alliance_id=0),
            Building(unique_id="enemy1", obj_type=27, alliance_id=200),
            Building(unique_id="fighting1", obj_type=48, alliance_id=0, fight_flag=1),
        ]
        snapshot = _make_snapshot(accounts=accounts, buildings=buildings)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        ids = [d.unique_id for d in view.building_details]
        assert ids[0] == "fighting1"   # 交战中最优先
        assert ids[1] == "enemy1"      # 然后敌方
        assert ids[2] == "neutral1"    # 然后中立
        assert ids[3] == "ally1"       # 最后我方

    def test_building_details_capped(self, config_2squads: AppConfig):
        """建筑详情不超过 MAX_BUILDING_DETAILS"""
        accounts = {i: _make_account(i, 100, 200) for i in range(1, 11)}
        buildings = [
            Building(unique_id=f"b{i}", obj_type=27, alliance_id=0)
            for i in range(30)
        ]
        snapshot = _make_snapshot(accounts=accounts, buildings=buildings)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert len(view.building_details) == L2ViewBuilder.MAX_BUILDING_DETAILS
        assert view.buildings.total == 30  # 摘要仍统计全部

    def test_no_buildings(self, config_2squads: AppConfig):
        """无建筑时不崩溃"""
        accounts = {i: _make_account(i, 100, 200) for i in range(1, 11)}
        snapshot = _make_snapshot(accounts=accounts)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert view.buildings.total == 0
        assert len(view.building_details) == 0


# ------------------------------------------------------------------
# 全局指标
# ------------------------------------------------------------------

class TestGlobalMetrics:
    def test_total_power_and_soldiers(self, config_2squads: AppConfig):
        """全局总战力和兵力正确汇总"""
        accounts = {i: _make_account(i, 100, 200, power=10000, soldiers=1000)
                    for i in range(1, 11)}
        snapshot = _make_snapshot(accounts=accounts)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert view.total_power == 100000
        assert view.total_soldiers == 10000

    def test_total_enemy_power(self, config_2squads: AppConfig):
        """敌方总战力正确汇总"""
        accounts = {i: _make_account(i, 100, 200) for i in range(1, 11)}
        enemies = [
            Enemy(uid=1001, city_pos=(300, 300), power=80000),
            Enemy(uid=1002, city_pos=(500, 500), power=60000),
        ]
        snapshot = _make_snapshot(accounts=accounts, enemies=enemies)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert view.total_enemy_power == 140000

    def test_army_center_weighted_by_power(self, config_2squads: AppConfig):
        """全军中心按战力加权"""
        accounts = {}
        # squad 1: 位置(100,100), 每人 power=10000, 总=50000
        for uid in range(1, 6):
            accounts[uid] = _make_account(uid, x=100, y=100, power=10000)
        # squad 2: 位置(300,300), 每人 power=30000, 总=150000
        for uid in range(6, 11):
            accounts[uid] = _make_account(uid, x=300, y=300, power=30000)
        snapshot = _make_snapshot(accounts=accounts)

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        # 加权中心: (100*50000 + 300*150000) / 200000 = 250
        assert view.army_center == (250, 250)

    def test_army_center_empty_squads(self, config_2squads: AppConfig):
        """无账号时全军中心为默认值"""
        snapshot = _make_snapshot()
        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert view.army_center == (500, 500)


# ------------------------------------------------------------------
# format_text 输出
# ------------------------------------------------------------------

class TestFormatText:
    def test_contains_key_sections(self, config_2squads: AppConfig):
        """markdown 包含所有关键段落"""
        accounts = {i: _make_account(i, 100, 200, power=10000) for i in range(1, 11)}
        enemies = [
            Enemy(uid=1001, city_pos=(300, 300), power=80000),
            Enemy(uid=1002, city_pos=(310, 310), power=70000),
        ]
        buildings = [Building(unique_id="b1", obj_type=27, alliance_id=0)]
        snapshot = _make_snapshot(
            accounts=accounts, enemies=enemies, buildings=buildings, loop_id=99,
        )

        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        text = builder.format_text(view)

        assert "Loop #99" in text
        assert "总体态势" in text
        assert "小队状态" in text
        assert "敌方威胁集群" in text
        assert "关键建筑" in text
        assert "Alpha" in text
        assert "Bravo" in text

    def test_empty_snapshot_format(self, config_2squads: AppConfig):
        """空快照也能正常格式化"""
        snapshot = _make_snapshot(loop_id=0)
        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        text = builder.format_text(view)
        assert "Loop #0" in text
        assert "未发现集群" in text
        assert "(无)" in text  # 无建筑


# ------------------------------------------------------------------
# 边界情况
# ------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_snapshot(self, config_2squads: AppConfig):
        """完全空的快照不崩溃"""
        snapshot = _make_snapshot()
        builder = L2ViewBuilder(config_2squads)
        view = builder.build(snapshot)
        assert view.total_power == 0
        assert view.total_enemy_power == 0
        assert len(view.enemy_clusters) == 0
        assert view.buildings.total == 0

    def test_no_alliance_config(self):
        """无联盟配置时建筑全部归为 enemy（非0非我方）"""
        config = AppConfig(
            accounts=AccountsConfig(
                accounts=[AccountEntry(uid=1, name="p1")],
            ),
            squads=SquadsConfig(alliances={"ours": AllianceSquadGroup(
                aid=0, name="default", squads=[
                    SquadEntry(squad_id=1, name="Solo", leader_uid=1, member_uids=[1]),
                ],
            )}),
            activity=ActivityConfig(),
            system=SystemConfig(),
        )
        buildings = [Building(unique_id="b1", obj_type=27, alliance_id=999)]
        accounts = {1: _make_account(1, 100, 200)}
        snapshot = _make_snapshot(accounts=accounts, buildings=buildings)

        builder = L2ViewBuilder(config)
        view = builder.build(snapshot)
        # alliance_id=0 → my_alliance_id, 999 != 0 → enemy
        assert view.buildings.enemy_held == 1
