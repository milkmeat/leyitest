"""数据同步 — 从游戏服务器并发获取原始数据

Phase 1 (Sync 0-5s) 的核心实现:
- 并发查询所有账号状态（get_player_info）
- 获取全图数据（get_map_brief_obj → 建筑 + 敌方玩家）
- 返回 SyncSnapshot 供下游 AI 层使用

设计要点:
- asyncio.Semaphore 控制并发（默认 20）
- 单账号失败不阻塞整体，记入 SyncSnapshot.errors
- 地图查询用任意一个成功账号的 uid 发起
- squad_id → group_id 映射从 config.squads 获取
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from src.config.schemas import AppConfig
from src.executor.game_api import GameAPIClient
from src.models.player_state import PlayerState
from src.models.building import Building
from src.models.enemy import Enemy

logger = logging.getLogger(__name__)

# 可作为建筑解析的 type 集合（普通地图）
BUILDING_TYPES = {27, 48, 64, 156}

# AVA 战场类型常量
AVA_PLAYER_TYPE = 10101          # AVA 玩家城市
AVA_BUILDING_TYPES = {10000, 10001, 10002, 10006, 10103, 10104}  # AVA 据点/建筑
AVA_RESOURCE_TYPES = {10300}     # AVA 资源点（暂忽略）


# ------------------------------------------------------------------
# 数据模型
# ------------------------------------------------------------------

class SyncError(BaseModel):
    """单个同步失败记录"""
    uid: int
    step: str          # "account" / "map"
    message: str


class SyncSnapshot(BaseModel):
    """一轮同步的完整快照 — 主循环下游的唯一输入"""
    accounts: dict[int, PlayerState] = Field(default_factory=dict)   # uid → PlayerState
    buildings: list[Building] = Field(default_factory=list)
    enemies: list[Enemy] = Field(default_factory=list)
    errors: list[SyncError] = Field(default_factory=list)
    sync_time: float = 0.0       # 同步耗时（秒）
    loop_id: int = 0


# ------------------------------------------------------------------
# 核心同步器
# ------------------------------------------------------------------

class DataSyncer:
    """数据同步器 — 并发获取账号 + 地图数据

    用法:
        syncer = DataSyncer(client, config)
        snapshot = await syncer.sync(loop_id=1)
    """

    def __init__(self, client: GameAPIClient, config: AppConfig):
        self.client = client
        self.config = config
        self._semaphore = asyncio.Semaphore(
            config.system.concurrency.max_api_concurrent
        )
        # 构建 uid → squad_id 映射
        self._uid_to_squad: dict[int, int] = {}
        for sq in config.squads.squads:
            for uid in sq.member_uids:
                self._uid_to_squad[uid] = sq.squad_id

    async def sync(self, loop_id: int = 0, lvl_id: int = 0) -> SyncSnapshot:
        """执行一轮完整同步

        Args:
            loop_id: 当前主循环编号
            lvl_id: AVA 战场 ID，非 0 时使用 AVA 地图 API

        Returns:
            SyncSnapshot 包含所有账号、建筑、敌方、错误信息
        """
        t0 = time.monotonic()
        timeout = self.config.system.loop.sync_timeout

        try:
            snapshot = await asyncio.wait_for(
                self._do_sync(loop_id, lvl_id=lvl_id), timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error("sync timeout after %ds (loop=%d)", timeout, loop_id)
            snapshot = SyncSnapshot(
                loop_id=loop_id,
                errors=[SyncError(uid=0, step="sync", message=f"整体超时 {timeout}s")],
            )

        snapshot.sync_time = round(time.monotonic() - t0, 3)
        return snapshot

    async def _do_sync(self, loop_id: int, lvl_id: int = 0) -> SyncSnapshot:
        """内部同步逻辑（无超时包装）"""
        errors: list[SyncError] = []

        # 1) 并发同步所有账号
        accounts, acct_errors = await self._sync_all_accounts()
        errors.extend(acct_errors)

        # 2) 同步地图 — 用第一个成功账号的 uid
        buildings: list[Building] = []
        enemies: list[Enemy] = []
        if accounts:
            first_uid = next(iter(accounts))
            try:
                if lvl_id != 0:
                    buildings, enemies = await self._sync_map_ava(first_uid, lvl_id)
                else:
                    buildings, enemies = await self._sync_map_both_sides(first_uid)
            except Exception as e:
                logger.error("map sync failed: %s", e)
                errors.append(SyncError(uid=first_uid, step="map", message=str(e)))

        return SyncSnapshot(
            accounts=accounts,
            buildings=buildings,
            enemies=enemies,
            errors=errors,
            loop_id=loop_id,
        )

    async def _sync_all_accounts(self) -> Tuple[dict[int, PlayerState], list[SyncError]]:
        """并发同步所有活跃账号"""
        uids = self.config.accounts.active_uids()
        tasks = [self._sync_account(uid) for uid in uids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        accounts: dict[int, PlayerState] = {}
        errors: list[SyncError] = []

        for uid, result in zip(uids, results):
            if isinstance(result, Exception):
                logger.warning("account sync failed uid=%d: %s", uid, result)
                errors.append(SyncError(uid=uid, step="account", message=str(result)))
            elif isinstance(result, SyncError):
                errors.append(result)
            elif isinstance(result, PlayerState):
                accounts[uid] = result
            else:
                errors.append(SyncError(uid=uid, step="account", message=f"unexpected result: {type(result)}"))

        return accounts, errors

    async def _sync_account(self, uid: int) -> PlayerState | SyncError:
        """同步单个账号（受 semaphore 限流）"""
        async with self._semaphore:
            try:
                info = await self.client.get_player_info(uid)
                group_id = self._uid_to_squad.get(uid, 0)
                return PlayerState.from_sync_info(info, group_id=group_id)
            except Exception as e:
                return SyncError(uid=uid, step="account", message=str(e))

    async def _sync_map_ava(
        self, uid: int, lvl_id: int,
    ) -> Tuple[list[Building], list[Enemy]]:
        """AVA 战场地图同步 — 使用 lvl_battle_login_get API

        AVA 地图返回结构与普通地图不同:
        - 数据在 svr_lvl_brief_objs.briefObjs（不是 briefList）
        - 对象是扁平结构（无 objBasic 嵌套），字段直接在顶层
        - 类型体系: 10101=玩家城市, 10000-10006=据点/建筑, 10300=资源点

        Args:
            uid: 用于发起查询的账号 UID
            lvl_id: AVA 战场 ID
        """
        async with self._semaphore:
            resp = await self.client.lvl_battle_login_get(uid, lvl_id)

        buildings: list[Building] = []
        enemies: list[Enemy] = []

        # 提取 data items — AVA 响应可能有多个 push_list 项，数据不一定在 [0]
        items: list[dict] = []
        try:
            for push in resp["res_data"][0]["push_list"]:
                items.extend(push.get("data", []))
        except (KeyError, IndexError, TypeError):
            logger.warning("AVA 地图响应结构异常")
            return buildings, enemies

        # 找到 svr_lvl_brief_objs 数据
        brief_data = None
        for item in items:
            name = item.get("name", "")
            if "svr_lvl_brief_objs" in name:
                raw = item.get("data", "")
                try:
                    brief_data = json.loads(raw) if isinstance(raw, str) else raw
                except (json.JSONDecodeError, TypeError):
                    continue
                break

        if not brief_data:
            logger.warning("未找到 svr_lvl_brief_objs 数据")
            return buildings, enemies

        # AVA 用 briefObjs 而不是 briefList
        brief_list = brief_data.get("briefObjs", brief_data.get("briefList", []))
        my_uids = set(self.config.accounts.all_uids())

        for obj in brief_list:
            # AVA 对象是扁平结构，type 直接在顶层
            obj_type = obj.get("type", 0)

            if obj_type == AVA_PLAYER_TYPE:
                # 玩家城市 — 排除我方
                # AVA 对象 uid 字段为 0，实际 UID 在 id 字段中
                obj_uid = int(obj.get("uid", 0)) or int(obj.get("id", 0))
                if obj_uid not in my_uids:
                    enemies.append(Enemy.from_brief_obj(obj))

            elif obj_type in AVA_BUILDING_TYPES:
                buildings.append(Building.from_brief_obj(obj))
            # type=10300 资源点暂时忽略

        logger.info("AVA map sync (lvl_id=%d): %d buildings, %d enemies",
                     lvl_id, len(buildings), len(enemies))
        return buildings, enemies

    async def _sync_map_both_sides(
        self, uid: int,
    ) -> Tuple[list[Building], list[Enemy]]:
        """分别用我方/敌方 aid 请求地图 brief，合并双方数据

        地图 brief API 按 header 中的 aid 过滤，只返回同联盟成员。
        因此需要两次请求：我方 aid 获取建筑，敌方 aid 获取敌方玩家。

        Args:
            uid: 用于发起查询的账号 UID
        """
        alliances = self.config.accounts.alliances
        enemy_aid_val = alliances.enemy.aid if alliances else 0

        # 并发请求：我方视角 + 敌方视角
        async with self._semaphore:
            tasks = [
                self.client.get_map_overview(uid, sid=1),
            ]
            if enemy_aid_val:
                enemy_uid = self.config.accounts.enemy_uids()[0] if self.config.accounts.enemy_uids() else uid
                tasks.append(
                    self.client.get_map_overview(
                        enemy_uid, sid=1,
                        header_overrides={"aid": enemy_aid_val},
                    )
                )
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # 解析我方视角 → 建筑 + (可能有的) 敌方
        buildings: list[Building] = []
        enemies: list[Enemy] = []

        our_resp = results[0]
        if not isinstance(our_resp, Exception):
            buildings, enemies = self._parse_map_response(our_resp)

        # 解析敌方视角 → 敌方玩家
        if len(results) > 1:
            enemy_resp = results[1]
            if not isinstance(enemy_resp, Exception):
                _, enemy_players = self._parse_map_response(enemy_resp)
                # 合并去重（敌方视角查到的覆盖我方视角）
                existing = {e.uid for e in enemies}
                for e in enemy_players:
                    if e.uid not in existing:
                        enemies.append(e)

        logger.info("map sync: %d buildings, %d enemies", len(buildings), len(enemies))
        return buildings, enemies

    def _parse_map_response(
        self, resp: dict,
    ) -> Tuple[list[Building], list[Enemy]]:
        """解析地图响应，提取建筑和非我方玩家

        敌我区分: 仅根据 UID 是否在 config.accounts 中判断，
        不依赖 alliance_id（测试账号联盟可能不统一）。

        响应结构: res_data[0].push_list[0].data 是 data item 列表，
        找到 name 含 "svr_map_brief" 的项，解析其 briefList。
        """
        buildings: list[Building] = []
        enemies: list[Enemy] = []

        # 提取 data items
        try:
            items = resp["res_data"][0]["push_list"][0]["data"]
        except (KeyError, IndexError, TypeError):
            logger.warning("地图响应结构异常")
            return buildings, enemies

        # 找到地图 brief 数据
        brief_data = None
        for item in items:
            name = item.get("name", "")
            if "svr_map_brief" in name:
                raw = item.get("data", "")
                try:
                    brief_data = json.loads(raw) if isinstance(raw, str) else raw
                except (json.JSONDecodeError, TypeError):
                    continue
                break

        if not brief_data:
            logger.warning("未找到 svr_map_brief 数据")
            return buildings, enemies

        # 解析 briefList
        brief_list = brief_data.get("briefList", brief_data.get("objs", []))
        # 我方账号 UID 集合 — 不在此集合中的 type=2 对象视为非我方玩家
        my_uids = set(self.config.accounts.all_uids())

        for obj in brief_list:
            basic = obj.get("objBasic", obj)  # 兼容扁平/嵌套格式
            obj_type = basic.get("type", 0)

            if obj_type == 2:
                # 玩家城市 — 不在我方 UID 集合中则归为非我方
                uid = int(basic.get("uid", 0))
                if uid not in my_uids:
                    enemies.append(Enemy.from_brief_obj(obj))

            elif obj_type in BUILDING_TYPES:
                buildings.append(Building.from_brief_obj(obj))

        return buildings, enemies

    async def sync_single_account(self, uid: int) -> PlayerState | SyncError:
        """同步单个账号（调试用，不受 semaphore 限制）"""
        try:
            info = await self.client.get_player_info(uid)
            group_id = self._uid_to_squad.get(uid, 0)
            return PlayerState.from_sync_info(info, group_id=group_id)
        except Exception as e:
            return SyncError(uid=uid, step="account", message=str(e))
