"""数据同步 — 从游戏服务器并发获取原始数据

Phase 1 (Sync 0-5s) 的核心实现:
- 并发查询所有账号状态（get_player_info）
- AVA 战场: lvl_battle_login_get 获取全图数据（建筑 + 敌方玩家）
- 普通地图: 仅同步各账号自身数据（game_server_login_get）
- 返回 SyncSnapshot 供下游 AI 层使用

设计要点:
- asyncio.Semaphore 控制并发（默认 20）
- 单账号失败不阻塞整体，记入 SyncSnapshot.errors
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

        # 2) 同步地图 — 仅 AVA 战场需要全图数据
        buildings: list[Building] = []
        enemies: list[Enemy] = []
        if accounts and lvl_id != 0:
            first_uid = next(iter(accounts))
            try:
                buildings, enemies = await self._sync_map_ava(first_uid, lvl_id)
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

    async def sync_single_account(self, uid: int) -> PlayerState | SyncError:
        """同步单个账号（调试用，不受 semaphore 限制）"""
        try:
            info = await self.client.get_player_info(uid)
            group_id = self._uid_to_squad.get(uid, 0)
            return PlayerState.from_sync_info(info, group_id=group_id)
        except Exception as e:
            return SyncError(uid=uid, step="account", message=str(e))

    async def _sync_map_ava_detail(
        self, uid: int, lvl_id: int,
        center_x: int, center_y: int, size: int = 10,
    ) -> Tuple[list[Building], list[Enemy]]:
        """AVA 战场详细地图同步 — 使用 lvl_svr_map_get API

        与 _sync_map_ava (lvl_battle_login_get, brief view) 的区别:
        - brief: 全局概要，扁平列表，只有基础字段
        - detail: 按 bid 分块，含丰富信息（城市等级/兵力/camp，建筑驻军数，行军类型）

        适用场景:
        - 需要精确驻军数据（判断建筑防御力）
        - 需要玩家兵力/camp 信息（判断敌我阵营）
        - 需要活跃行军信息（侦测敌方调动）

        Args:
            uid: 查询账号 UID
            lvl_id: 战场 ID
            center_x, center_y: 查询中心坐标（像素）
            size: 范围边长（地块数，默认 10x10）
        """
        my_uids = set(self.config.accounts.all_uids())

        async with self._semaphore:
            map_objs = await self.client.lvl_get_map_area(
                uid, lvl_id, center_x, center_y, size,
            )

        buildings: list[Building] = []
        enemies: list[Enemy] = []

        for block in map_objs:
            for obj in block.get("objs", []):
                basic = obj.get("objBasic", {})
                obj_type = basic.get("type", 0)

                if obj_type == AVA_PLAYER_TYPE:
                    obj_uid = int(basic.get("uid", 0)) or int(basic.get("id", 0))
                    if obj_uid not in my_uids:
                        enemies.append(Enemy.from_brief_obj(obj))

                elif obj_type in AVA_BUILDING_TYPES:
                    buildings.append(Building.from_brief_obj(obj))
                # type=101 (行军) 和 type=10300 (资源点) 暂时忽略

        logger.info(
            "AVA detail map sync (lvl_id=%d, center=%d,%d, size=%d): %d buildings, %d enemies",
            lvl_id, center_x, center_y, size, len(buildings), len(enemies),
        )
        return buildings, enemies
