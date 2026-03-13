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

# 可作为建筑解析的 type 集合
BUILDING_TYPES = {27, 48, 64, 156}


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

    async def sync(self, loop_id: int = 0) -> SyncSnapshot:
        """执行一轮完整同步

        Args:
            loop_id: 当前主循环编号

        Returns:
            SyncSnapshot 包含所有账号、建筑、敌方、错误信息
        """
        t0 = time.monotonic()
        timeout = self.config.system.loop.sync_timeout

        try:
            snapshot = await asyncio.wait_for(
                self._do_sync(loop_id), timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error("sync timeout after %ds (loop=%d)", timeout, loop_id)
            snapshot = SyncSnapshot(
                loop_id=loop_id,
                errors=[SyncError(uid=0, step="sync", message=f"整体超时 {timeout}s")],
            )

        snapshot.sync_time = round(time.monotonic() - t0, 3)
        return snapshot

    async def _do_sync(self, loop_id: int) -> SyncSnapshot:
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
                buildings, enemies = await self._sync_map(first_uid)
            except Exception as e:
                logger.error("map sync failed: %s", e)
                errors.append(SyncError(uid=first_uid, step="map", message=str(e)))
        else:
            errors.append(SyncError(uid=0, step="map", message="无可用账号，跳过地图同步"))

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

    async def _sync_map(
        self, uid: int,
    ) -> Tuple[list[Building], list[Enemy]]:
        """同步地图概览，解析建筑和非我方玩家

        Args:
            uid: 用于发起查询的账号 UID
        """
        async with self._semaphore:
            resp = await self.client.get_map_overview(uid, sid=1)

        return self._parse_map_response(resp)

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
