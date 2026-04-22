"""L0 执行层 — AI 指令翻译与校验

职责:
1. 将 AI 语义指令 (MOVE_CITY 等) 映射为 game_api 便捷方法调用
2. 预校验: UID 合法、坐标范围、必填参数
3. 返回 ExecutionResult 供 L1 反馈

用法:
    executor = L0Executor(client, config)
    result = await executor.execute(AIInstruction(action="MOVE_CITY", uid=123, target_x=500, target_y=500))
"""

from __future__ import annotations

import json as _json
import logging
import math
import random
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel

from src.executor.game_api import GameAPIClient
from src.config.schemas import AppConfig
from src.models.player_state import PlayerState, TroopState
from src.utils.coords import encode_pos, decode_pos, make_bid_list

logger = logging.getLogger(__name__)

# 惰性加载的错误码表 (ret_code → message)
_error_msg_cache: Optional[Dict[int, str]] = None


def _load_error_msgs() -> Dict[int, str]:
    """加载 error_msg.yaml 错误码表（只加载一次）"""
    global _error_msg_cache
    if _error_msg_cache is not None:
        return _error_msg_cache
    import yaml
    from pathlib import Path
    yaml_path = Path(__file__).parent.parent.parent / "docs" / "p10" / "error_msg.yaml"
    if yaml_path.exists():
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        _error_msg_cache = {int(k): str(v) for k, v in data.items()} if isinstance(data, dict) else {}
    else:
        _error_msg_cache = {}
    return _error_msg_cache


def _lookup_error(ret_code: int) -> str:
    """查表翻译 ret_code 为可读消息"""
    msgs = _load_error_msgs()
    msg = msgs.get(ret_code, "")
    return f" ({msg})" if msg else ""


# ------------------------------------------------------------------
# AI 指令数据结构（L1 LLM 输出 JSON 直接反序列化）
# ------------------------------------------------------------------

class ActionType(str, Enum):
    # --- 主世界指令 ---
    MOVE_CITY = "MOVE_CITY"
    ATTACK_TARGET = "ATTACK_TARGET"
    SCOUT = "SCOUT"
    GARRISON_BUILDING = "GARRISON_BUILDING"
    INITIATE_RALLY = "INITIATE_RALLY"
    JOIN_RALLY = "JOIN_RALLY"
    RETREAT = "RETREAT"
    RALLY_DISMISS = "RALLY_DISMISS"
    RECALL_REINFORCE = "RECALL_REINFORCE"
    # --- AVA 战场内指令 ---
    LVL_MOVE_CITY = "LVL_MOVE_CITY"
    LVL_ATTACK_PLAYER = "LVL_ATTACK_PLAYER"
    LVL_ATTACK_BUILDING = "LVL_ATTACK_BUILDING"
    LVL_REINFORCE_BUILDING = "LVL_REINFORCE_BUILDING"
    LVL_SCOUT_PLAYER = "LVL_SCOUT_PLAYER"
    LVL_SCOUT_BUILDING = "LVL_SCOUT_BUILDING"
    LVL_INITIATE_RALLY = "LVL_INITIATE_RALLY"
    LVL_INITIATE_RALLY_BUILDING = "LVL_INITIATE_RALLY_BUILDING"
    LVL_JOIN_RALLY = "LVL_JOIN_RALLY"
    LVL_RALLY_DISMISS = "LVL_RALLY_DISMISS"
    LVL_RECALL_REINFORCE = "LVL_RECALL_REINFORCE"
    LVL_RECALL_TROOP = "LVL_RECALL_TROOP"
    LVL_SPEED_UP = "LVL_SPEED_UP"
    LVL_RECALL_FROM_BUILDING = "LVL_RECALL_FROM_BUILDING"


class AIInstruction(BaseModel):
    """L1 LLM 输出的单条行动指令

    使用方式: AIInstruction.model_validate_json(json_str)
    """
    action: ActionType
    uid: int                           # 执行账号
    target_x: int = 0                  # 目标坐标
    target_y: int = 0
    target_uid: int = 0                # 目标玩家 UID
    building_id: str = ""              # 建筑 unique_id
    rally_id: str = ""                 # 集结 ID（JOIN_RALLY / LVL_JOIN_RALLY）
    troop_ids: list[str] = []          # 部队 ID 列表（RETREAT / LVL_RECALL_FROM_BUILDING）
    prepare_time: int = 300            # 集结准备时间秒（INITIATE_RALLY 默认300, LVL 默认60）
    reinforce_id: str = ""             # 增援部队 unique_id（RECALL_REINFORCE 用）
    troop_unique_id: str = ""          # 队伍唯一 ID（LVL_SPEED_UP / LVL_RECALL_TROOP / LVL_RECALL_REINFORCE）
    building_key: int = 0              # 建筑 key（LVL 战场建筑操作用）
    soldier_id: int = 0                # 手动指定兵种ID（0=自动选择）
    soldier_count: int = 0             # 手动指定出征数量（0=默认）
    override_queue_id: int = 0         # L0 回退队列覆盖（0=按默认规则）
    reason: str = ""                   # L1 决策理由（日志用）


class ExecutionResult(BaseModel):
    """单条指令的执行结果"""
    success: bool
    action: ActionType
    uid: int
    message: str = ""                  # 人类可读结果描述
    error: str = ""                    # 校验/执行错误信息
    server_response: Dict[str, Any] = {}  # 原始服务器返回（debug 用）


# ------------------------------------------------------------------
# L0 执行器
# ------------------------------------------------------------------

class L0Executor:
    """将 AIInstruction 翻译为 GameAPIClient 调用

    流程: validate → 翻译参数 → 调用 game_api → 包装 ExecutionResult
    """

    def __init__(self, client: GameAPIClient, config: AppConfig):
        self.client = client
        self.valid_uids = config.accounts.all_uids()
        self.map_width = config.activity.map.width
        self.map_height = config.activity.map.height
        # 我方联盟 ID（AVA 用 lvl_aid，主世界用 aid）
        alliances = config.accounts.alliances
        if alliances and alliances.ours.lvl_aid:
            self._my_alliance_id = alliances.ours.lvl_aid
        elif alliances:
            self._my_alliance_id = alliances.ours.aid
        else:
            self._my_alliance_id = 0

    def validate(self, instr: AIInstruction) -> tuple[bool, str]:
        """预校验指令参数

        Returns:
            (True, "") 表示通过，(False, "错误描述") 表示失败
        """
        # UID 合法性
        if instr.uid not in self.valid_uids:
            return False, f"UID {instr.uid} 不在配置的账号列表中"

        # 需要坐标的指令: 检查范围
        needs_coords = {
            ActionType.MOVE_CITY,
            ActionType.ATTACK_TARGET,
            ActionType.SCOUT,
            ActionType.GARRISON_BUILDING,
            ActionType.INITIATE_RALLY,
            ActionType.LVL_MOVE_CITY,
            ActionType.LVL_ATTACK_PLAYER,
            ActionType.LVL_ATTACK_BUILDING,
            ActionType.LVL_SCOUT_PLAYER,
            ActionType.LVL_SCOUT_BUILDING,
            ActionType.LVL_INITIATE_RALLY,
            ActionType.LVL_INITIATE_RALLY_BUILDING,
        }
        if instr.action in needs_coords:
            if not (0 <= instr.target_x < self.map_width):
                return False, (
                    f"target_x={instr.target_x} 超出地图范围 [0, {self.map_width})"
                )
            if not (0 <= instr.target_y < self.map_height):
                return False, (
                    f"target_y={instr.target_y} 超出地图范围 [0, {self.map_height})"
                )

        # 各指令的必填参数
        if instr.action == ActionType.ATTACK_TARGET:
            if instr.target_uid <= 0 and not instr.building_id:
                return False, "ATTACK_TARGET 需要 target_uid > 0 或 building_id 非空"

        elif instr.action == ActionType.SCOUT:
            if instr.target_uid <= 0:
                return False, "SCOUT 需要 target_uid > 0"

        elif instr.action == ActionType.GARRISON_BUILDING:
            if not instr.building_id:
                return False, "GARRISON_BUILDING 需要 building_id 非空"

        elif instr.action == ActionType.JOIN_RALLY:
            if not instr.rally_id:
                return False, "JOIN_RALLY 需要 rally_id 非空"

        elif instr.action == ActionType.RETREAT:
            if not instr.troop_ids:
                return False, "RETREAT 需要 troop_ids 非空"

        elif instr.action == ActionType.RALLY_DISMISS:
            if not instr.rally_id:
                return False, "RALLY_DISMISS 需要 rally_id 非空"

        elif instr.action == ActionType.RECALL_REINFORCE:
            if not instr.reinforce_id:
                return False, "RECALL_REINFORCE 需要 reinforce_id 非空"

        # --- AVA 战场指令校验 ---
        elif instr.action == ActionType.LVL_ATTACK_PLAYER:
            if instr.target_uid <= 0:
                return False, "LVL_ATTACK_PLAYER 需要 target_uid > 0"

        elif instr.action == ActionType.LVL_ATTACK_BUILDING:
            if not instr.building_id:
                return False, "LVL_ATTACK_BUILDING 需要 building_id 非空"

        elif instr.action == ActionType.LVL_REINFORCE_BUILDING:
            if not instr.building_id:
                return False, "LVL_REINFORCE_BUILDING 需要 building_id 非空"

        elif instr.action == ActionType.LVL_SCOUT_PLAYER:
            if instr.target_uid <= 0:
                return False, "LVL_SCOUT_PLAYER 需要 target_uid > 0"

        elif instr.action == ActionType.LVL_SCOUT_BUILDING:
            if not instr.building_id:
                return False, "LVL_SCOUT_BUILDING 需要 building_id 非空"

        elif instr.action == ActionType.LVL_INITIATE_RALLY:
            if instr.target_uid <= 0:
                return False, "LVL_INITIATE_RALLY 需要 target_uid > 0"

        elif instr.action == ActionType.LVL_INITIATE_RALLY_BUILDING:
            if not instr.building_id:
                return False, "LVL_INITIATE_RALLY_BUILDING 需要 building_id 非空"

        elif instr.action == ActionType.LVL_JOIN_RALLY:
            if not instr.rally_id:
                return False, "LVL_JOIN_RALLY 需要 rally_id 非空"

        elif instr.action == ActionType.LVL_RALLY_DISMISS:
            if not instr.rally_id:
                return False, "LVL_RALLY_DISMISS 需要 rally_id 非空"

        elif instr.action == ActionType.LVL_RECALL_REINFORCE:
            if not instr.troop_unique_id:
                return False, "LVL_RECALL_REINFORCE 需要 troop_unique_id 非空"

        elif instr.action == ActionType.LVL_RECALL_TROOP:
            if not instr.troop_unique_id:
                return False, "LVL_RECALL_TROOP 需要 troop_unique_id 非空"

        elif instr.action == ActionType.LVL_SPEED_UP:
            if not instr.troop_unique_id:
                return False, "LVL_SPEED_UP 需要 troop_unique_id 非空"

        elif instr.action == ActionType.LVL_RECALL_FROM_BUILDING:
            if not instr.troop_ids:
                return False, "LVL_RECALL_FROM_BUILDING 需要 troop_ids 非空"

        return True, ""

    async def execute(self, instr: AIInstruction, rally_pos: str = "") -> ExecutionResult:
        """校验 → 翻译 → 调用 game_api → 返回结果

        Args:
            instr: AI 指令
            rally_pos: 集结对象的编码坐标（JOIN_RALLY 用，同循环回填）
        """
        # 1. 校验
        ok, err_msg = self.validate(instr)
        if not ok:
            logger.warning("L0 校验失败: %s — %s", instr.action.value, err_msg)
            return ExecutionResult(
                success=False, action=instr.action, uid=instr.uid, error=err_msg,
            )

        # 2. 执行
        try:
            resp = await self._dispatch(instr, rally_pos=rally_pos)
            # 判断服务器返回码
            ret_code = resp.get("res_header", {}).get("ret_code", -1)
            if ret_code == 0:
                msg = self._success_message(instr)
                logger.info("L0 执行成功: %s uid=%s — %s", instr.action.value, instr.uid, msg)
                return ExecutionResult(
                    success=True, action=instr.action, uid=instr.uid,
                    message=msg, server_response=resp,
                )
            else:
                err = resp.get("res_header", {}).get("err_msg", f"ret_code={ret_code}")
                err_detail = _lookup_error(ret_code)
                logger.warning("L0 服务器返回错误: %s uid=%s — %s%s", instr.action.value, instr.uid, err, err_detail)
                return ExecutionResult(
                    success=False, action=instr.action, uid=instr.uid,
                    error=err, server_response=resp,
                )
        except Exception as e:
            logger.error("L0 执行异常: %s uid=%s — %s", instr.action.value, instr.uid, e)
            return ExecutionResult(
                success=False, action=instr.action, uid=instr.uid,
                error=str(e),
            )

    async def execute_batch(
        self,
        instructions: list[AIInstruction],
        accounts: Optional[dict[int, PlayerState]] = None,
        buildings: Optional[list] = None,
    ) -> list[ExecutionResult]:
        """顺序执行一批指令（不并发，避免同一账号竞态）

        支持：
        - 自动构建 march_info（从 accounts 获取兵力/英雄数据）
        - 同循环 Rally：INITIATE_RALLY 成功后自动提取 rally_id，
          回填到后续 rally_id 为空的 JOIN_RALLY 指令
        - 建筑归属预检查：INITIATE_RALLY 前检查目标是否已是我方建筑
        - 28003 恢复：INITIATE 失败时查询已有集结或转为 REINFORCE
        """
        self._accounts = accounts or {}
        self._buildings = {b.unique_id: b for b in (buildings or [])}
        self._inflight_queues: dict[int, set[int]] = {}  # uid → 本批次已消耗的 queue_id
        results = []
        # 最近一次成功的 rally 信息（同循环回填用）
        last_rally_id: str = ""
        last_rally_pos: str = ""
        # 最近一次 INITIATE 的目标信息（用于补全 JOIN 的坐标）
        last_initiate_target: dict = {}  # {target_x, target_y, building_id}
        # 当 INITIATE 目标已是我方建筑且无活跃集结时，后续 JOIN 转为 REINFORCE
        _convert_join_to_reinforce: str = ""

        _rally_actions = {ActionType.JOIN_RALLY, ActionType.LVL_JOIN_RALLY}
        _initiate_actions = {
            ActionType.INITIATE_RALLY,
            ActionType.LVL_INITIATE_RALLY,
            ActionType.LVL_INITIATE_RALLY_BUILDING,
        }

        for instr in instructions:
            # ── 通用队列占用预检查 ──
            # 仅对出征类指令检查（排除 RETREAT/RECALL/MOVE_CITY 等非出征操作）
            required_queue = self._get_queue_id_for_action(instr.action)
            if required_queue > 0:
                queue_occupied = self._is_queue_occupied(instr.uid, required_queue)
                if queue_occupied:
                    fallback = self._find_fallback_queue(instr.action, instr.uid)
                    if fallback:
                        instr = instr.model_copy(update={"override_queue_id": fallback})
                        logger.info(
                            "L0 队列回退: uid=%d queue %d occupied, 使用 fallback %d (%s)",
                            instr.uid, required_queue, fallback, instr.action.value,
                        )
                    else:
                        reason = (
                            f"SKIP: uid={instr.uid} queue {required_queue} occupied, "
                            f"no fallback ({instr.action.value})"
                        )
                        logger.info("L0 队列预检查跳过: %s", reason)
                        results.append(ExecutionResult(
                            success=False, action=instr.action, uid=instr.uid,
                            error=reason,
                        ))
                        continue

            # 补全 JOIN_RALLY 的缺失坐标（从最近的 INITIATE 目标推断）
            if (instr.action in _rally_actions
                    and not instr.target_x and not instr.target_y
                    and last_initiate_target):
                instr = instr.model_copy(update={
                    "target_x": last_initiate_target.get("target_x", 0),
                    "target_y": last_initiate_target.get("target_y", 0),
                })
                logger.info(
                    "L0 补全 JOIN 坐标: uid=%d → (%d,%d) from last INITIATE",
                    instr.uid, instr.target_x, instr.target_y,
                )

            # 自动回填 rally_id 和坐标
            if (instr.action in _rally_actions
                    and not instr.rally_id and last_rally_id):
                instr = instr.model_copy(update={"rally_id": last_rally_id})
                logger.info("自动回填 rally_id=%s → uid=%d", last_rally_id, instr.uid)

            # Fix 4: JOIN_RALLY 转 REINFORCE（目标建筑已是我方且无集结）
            if (instr.action in _rally_actions
                    and not instr.rally_id
                    and _convert_join_to_reinforce):
                bid = _convert_join_to_reinforce
                new_action = (ActionType.LVL_REINFORCE_BUILDING
                              if instr.action == ActionType.LVL_JOIN_RALLY
                              else ActionType.REINFORCE_BUILDING)
                instr = instr.model_copy(update={
                    "action": new_action,
                    "building_id": bid,
                })
                logger.info(
                    "L0 JOIN→REINFORCE: uid=%d 建筑 %s 已是我方, 转为驻防",
                    instr.uid, bid,
                )

            # Fix 2: 无前置 INITIATE 的 JOIN_RALLY → 自动转为 INITIATE
            # 当小队只有 JOIN 没有 INITIATE 时（跨小队 JOIN 场景），
            # 将第一个 JOIN 转为 INITIATE，让小队自己发起集结
            if (instr.action in _rally_actions
                    and not instr.rally_id
                    and not _convert_join_to_reinforce
                    and instr.target_x and instr.target_y):
                # 需要 building_id 来发起集结，尝试从坐标匹配建筑
                matched_bid = self._find_building_by_pos(
                    instr.target_x, instr.target_y,
                )
                if matched_bid:
                    new_action = (ActionType.LVL_INITIATE_RALLY_BUILDING
                                  if instr.action == ActionType.LVL_JOIN_RALLY
                                  else ActionType.INITIATE_RALLY)
                    instr = instr.model_copy(update={
                        "action": new_action,
                        "building_id": matched_bid,
                    })
                    logger.info(
                        "L0 JOIN→INITIATE: uid=%d 无前置集结, "
                        "自动转为发起集结 building=%s",
                        instr.uid, matched_bid,
                    )

            # Smart L0: 发起集结前的预处理
            if instr.action in _initiate_actions:
                # 记录 INITIATE 目标信息，供后续 JOIN 补全坐标
                tx, ty = instr.target_x, instr.target_y
                # 如果 INITIATE 没有坐标，从 buildings 中获取
                if (not tx and not ty) and instr.building_id and self._buildings:
                    bld = self._buildings.get(instr.building_id)
                    if bld:
                        tx, ty = bld.pos
                last_initiate_target = {
                    "target_x": tx,
                    "target_y": ty,
                    "building_id": instr.building_id,
                }

                # Fix 4: 建筑归属预检查 — INITIATE 前检查目标是否已是我方建筑
                if instr.building_id and self._buildings:
                    target_bld = self._buildings.get(instr.building_id)
                    if (target_bld
                            and self._my_alliance_id
                            and target_bld.alliance_id == self._my_alliance_id):
                        # 建筑已是我方的，尝试查询已有集结
                        rid, rpos = await self._query_rally_by_target(
                            instr.uid, instr.building_id,
                        )
                        if rid:
                            last_rally_id = rid
                            last_rally_pos = rpos
                            logger.info(
                                "L0 建筑归属预检查: %s 已是我方建筑, "
                                "找到已有集结 rally_id=%s, 跳过 INITIATE",
                                instr.building_id, rid,
                            )
                            results.append(ExecutionResult(
                                success=False, action=instr.action, uid=instr.uid,
                                error=f"建筑 {instr.building_id} 已是我方, 复用集结 {rid}",
                            ))
                        else:
                            logger.info(
                                "L0 建筑归属预检查: %s 已是我方建筑且无活跃集结, "
                                "后续 JOIN 将转为 REINFORCE",
                                instr.building_id,
                            )
                            # 标记: 后续 JOIN 应转为 REINFORCE
                            last_rally_id = ""
                            last_rally_pos = ""
                            _convert_join_to_reinforce = instr.building_id
                            results.append(ExecutionResult(
                                success=False, action=instr.action, uid=instr.uid,
                                error=f"建筑 {instr.building_id} 已是我方且无集结, 转 REINFORCE",
                            ))
                        continue

            # Smart L0: LVL_ATTACK_BUILDING / LVL_REINFORCE_BUILDING 预处理（距离检查 + 部队去重）
            original_attack_instr: AIInstruction | None = None
            if instr.action in (ActionType.LVL_ATTACK_BUILDING, ActionType.LVL_REINFORCE_BUILDING):
                processed, skip_reason = await self._preprocess_lvl_attack_building(instr)
                if processed is None:
                    results.append(ExecutionResult(
                        success=True, action=instr.action, uid=instr.uid,
                        message=skip_reason,
                    ))
                    continue
                # 记录原始攻击指令，用于移城失败重试
                if processed.action == ActionType.LVL_MOVE_CITY:
                    original_attack_instr = instr
                instr = processed

            result = await self.execute(instr, rally_pos=last_rally_pos)

            # Smart L0: 移城失败重试（随机偏移坐标）
            if (not result.success
                    and instr.action == ActionType.LVL_MOVE_CITY):
                result = await self._retry_move_city(
                    instr, original_attack_instr or instr,
                )

            # Smart L0: 移城成功后自动追击（消除浪费的 loop 周期）
            if (result.success
                    and instr.action == ActionType.LVL_MOVE_CITY
                    and original_attack_instr is not None):
                # 更新缓存的城市坐标，避免二次距离检查再触发移城
                acct = self._accounts.get(instr.uid)
                if acct:
                    acct.city_pos = (instr.target_x, instr.target_y)
                # 重新预处理原始指令（处理归属变化、部队去重）
                follow_instr, skip_reason = await self._preprocess_lvl_attack_building(
                    original_attack_instr,
                )
                if follow_instr and follow_instr.action != ActionType.LVL_MOVE_CITY:
                    follow_result = await self.execute(
                        follow_instr, rally_pos=last_rally_pos,
                    )
                    logger.info(
                        "L0 移城后追击: uid=%d %s building=%s success=%s",
                        instr.uid, follow_instr.action.value,
                        follow_instr.building_id, follow_result.success,
                    )
                    result = follow_result
                elif skip_reason:
                    logger.info(
                        "L0 移城后追击跳过: uid=%d %s",
                        instr.uid, skip_reason,
                    )

            results.append(result)

            # 批次内队列追踪: 记录成功消耗的 queue_id
            if result.success:
                consumed_q = self._get_queue_id_for_action(instr.action)
                if consumed_q > 0:
                    actual_q = instr.override_queue_id or consumed_q
                    self._inflight_queues.setdefault(instr.uid, set()).add(actual_q)

            # 从 INITIATE_RALLY / LVL_INITIATE_RALLY 响应中提取 rally_id 和 pos
            if result.success and instr.action in _initiate_actions:
                # 先尝试从响应中直接提取（Mock 服务器）
                rid, rpos = self._extract_rally_info(result.server_response)
                # 真实服务器不在 HTTP 响应中返回 rally_id，需要主动查询
                lvl_id = self.client.default_header.get("lvl_id", 0)
                if not rid and lvl_id:
                    rid, rpos = await self._query_rally_id(instr.uid)
                if rid:
                    last_rally_id = rid
                    last_rally_pos = rpos
                    _convert_join_to_reinforce = ""  # 清除转 REINFORCE 标记
                    logger.info("提取 rally_id=%s pos=%s from %s uid=%d",
                                rid, rpos, instr.action.value, instr.uid)

            # Fix 1: INITIATE 返回 28003 ("target is your ally") 恢复机制
            if (not result.success
                    and instr.action in _initiate_actions
                    and result.server_response.get("res_header", {}).get("ret_code") == 28003):
                target_id = instr.building_id
                if target_id:
                    self._mark_building_as_ours(target_id)
                    rid, rpos = await self._query_rally_by_target(instr.uid, target_id)
                    if rid:
                        last_rally_id = rid
                        last_rally_pos = rpos
                        _convert_join_to_reinforce = ""
                        logger.info(
                            "28003 恢复: 建筑 %s 已是我方, 找到已有集结 rally_id=%s",
                            target_id, rid,
                        )
                    else:
                        # 无活跃集结，后续 JOIN 转为 REINFORCE
                        _convert_join_to_reinforce = target_id
                        logger.info(
                            "28003 恢复: 建筑 %s 已是我方且无集结, 后续 JOIN 转 REINFORCE",
                            target_id,
                        )

            # Fix 5: LVL_ATTACK_BUILDING 返回 28003 — 转为 REINFORCE 重试
            if (not result.success
                    and instr.action == ActionType.LVL_ATTACK_BUILDING
                    and result.server_response.get("res_header", {}).get("ret_code") == 28003):
                target_id = instr.building_id
                if target_id:
                    self._mark_building_as_ours(target_id)
                    reinforce_instr = instr.model_copy(update={
                        "action": ActionType.LVL_REINFORCE_BUILDING,
                        "reason": f"28003 恢复: 建筑 {target_id} 已是我方, 转为驻防",
                    })
                    logger.info(
                        "28003 恢复: LVL_ATTACK_BUILDING→LVL_REINFORCE_BUILDING "
                        "uid=%d building=%s",
                        instr.uid, target_id,
                    )
                    reinforce_result = await self.execute(reinforce_instr)
                    # 无论成功与否都替换结果，日志可追踪恢复尝试
                    results[-1] = reinforce_result

        # ── 自动采集 coal cart (AVA only) ──
        _move_actions = {ActionType.MOVE_CITY, ActionType.LVL_MOVE_CITY}
        eligible_uids: set[int] = set()
        for r, i in zip(results, instructions):
            if r.success and i.action not in _move_actions:
                eligible_uids.add(i.uid)
        if eligible_uids:
            await self._auto_collect_coal_carts(eligible_uids)

        return results

    async def _query_rally_id(self, uid: int) -> tuple[str, str]:
        """通过 lvl_battle_login_get 查询当前用户发起的集结 rally_id

        优先从 svr_lvl_rally（rally brief）中查找 ownerUid 匹配的集结。
        回退到 svr_lvl_user_objs 的 cityInfo.mainTroopUniqueId。

        Returns:
            (rally_unique_id, rally_pos_encoded) — 失败时返回 ("", "")
        """
        lvl_id = self.client.default_header.get("lvl_id", 0)
        if not lvl_id:
            return "", ""
        try:
            resp = await self.client.lvl_battle_login_get(uid, lvl_id)
            for res in resp.get("res_data", []):
                for push in res.get("push_list", []):
                    for item in push.get("data", []):
                        name = item.get("name", "")
                        raw = item.get("data", "")

                        # 优先: svr_lvl_rally → brief[].ownerUid 匹配
                        if "svr_lvl_rally" in name:
                            data = _json.loads(raw) if isinstance(raw, str) else raw
                            for brief in data.get("brief", []):
                                if str(brief.get("ownerUid")) == str(uid):
                                    rid = brief.get("uniqueId", "")
                                    rpos = str(brief.get("pos", ""))
                                    logger.info("从 svr_lvl_rally 查到 rally: %s pos=%s", rid, rpos)
                                    return rid, rpos

                        # 回退: svr_lvl_user_objs → cityInfo.mainTroopUniqueId
                        if "svr_lvl_user_objs" in name:
                            data = _json.loads(raw) if isinstance(raw, str) else raw
                            for obj in data.get("objs", []):
                                basic = obj.get("objBasic", {})
                                if basic.get("type") == 10101 and str(basic.get("id")) == str(uid):
                                    city = obj.get("cityInfo", {})
                                    main_troop = city.get("mainTroopUniqueId", "")
                                    if main_troop:
                                        rpos = str(basic.get("pos", ""))
                                        logger.info("从 user_objs 查到 rally troop: %s pos=%s", main_troop, rpos)
                                        return main_troop, rpos
        except Exception as e:
            logger.warning("查询 rally_id 失败: %s", e)
        return "", ""

    # ------------------------------------------------------------------
    # 队列占用检查
    # ------------------------------------------------------------------

    # 出征类 action → 默认 queue_id 映射
    _INITIATE_Q_ACTIONS = {
        ActionType.INITIATE_RALLY,
        ActionType.LVL_INITIATE_RALLY,
        ActionType.LVL_INITIATE_RALLY_BUILDING,
    }
    _JOIN_Q_ACTIONS = {
        ActionType.JOIN_RALLY,
        ActionType.LVL_JOIN_RALLY,
    }
    # 非出征类 action（不占用队列）
    _NON_DISPATCH_ACTIONS = {
        ActionType.RETREAT,
        ActionType.LVL_RECALL_TROOP,
        ActionType.LVL_RECALL_FROM_BUILDING,
        ActionType.LVL_RECALL_REINFORCE,
        ActionType.LVL_SPEED_UP,
        ActionType.MOVE_CITY,
        ActionType.LVL_MOVE_CITY,
        ActionType.SCOUT,
    }

    def _get_queue_id_for_action(self, action: ActionType) -> int:
        """返回 action 对应的默认 queue_id，非出征类返回 0"""
        if action in self._NON_DISPATCH_ACTIONS:
            return 0
        if action in self._INITIATE_Q_ACTIONS:
            return 6002
        if action in self._JOIN_Q_ACTIONS:
            return 6004
        return 6001  # solo: attack, reinforce, garrison 等

    def _is_queue_occupied(self, uid: int, queue_id: int) -> bool:
        """检查指定账号的 queue_id 是否已被占用（含批次内 inflight）"""
        # 1. 检查 sync 数据中的部队
        acct = self._accounts.get(uid)
        if acct:
            for t in acct.troops:
                if t.state != TroopState.IDLE and t.queue_id == queue_id:
                    return True
        # 2. 检查本批次已消耗的队列
        if queue_id in self._inflight_queues.get(uid, set()):
            return True
        return False

    def _find_fallback_queue(self, action: ActionType, uid: int) -> int:
        """为被占用的队列寻找回退 queue_id

        回退规则:
        - JOIN_RALLY (6004 occupied): 依次尝试 6003 → 6002
        - INITIATE_RALLY (6002 occupied): 无回退（L1 应选其他队员）
        - Solo (6001 occupied): 无回退

        Returns:
            可用的 fallback queue_id，无回退返回 0
        """
        if action in self._JOIN_Q_ACTIONS:
            for fallback in [6003, 6002]:
                if not self._is_queue_occupied(uid, fallback):
                    return fallback
        return 0

    def _find_building_by_pos(self, x: int, y: int) -> str:
        """根据坐标查找最近的建筑 unique_id

        用于 Fix 2: JOIN_RALLY 转 INITIATE 时需要 building_id。
        Returns:
            building unique_id，未找到返回 ""
        """
        if not self._buildings:
            return ""
        best_bid = ""
        best_dist = float("inf")
        for bid, bld in self._buildings.items():
            bx, by = bld.pos
            dist = abs(bx - x) + abs(by - y)
            if dist < best_dist:
                best_dist = dist
                best_bid = bid
        # 只在距离合理时返回（坐标应该非常接近）
        if best_dist <= 5:
            return best_bid
        return ""

    def _mark_building_as_ours(self, building_id: str) -> None:
        """28003 后更新缓存: 将建筑标记为我方

        当服务器返回 28003 ("target is your ally")，说明建筑在同步后
        已被己方占领。更新缓存使同批次后续命令能被 Fix 4 预检查拦截。
        """
        bld = self._buildings.get(building_id)
        if bld and self._my_alliance_id:
            self._buildings[building_id] = bld.model_copy(
                update={"alliance_id": self._my_alliance_id}
            )
            logger.info(
                "L0 缓存更新: 建筑 %s 标记为我方 (alliance_id=%d)",
                building_id, self._my_alliance_id,
            )

    async def _query_rally_by_target(
        self, uid: int, target_id: str,
    ) -> tuple[str, str]:
        """查询指定目标建筑上的活跃集结

        通过 lvl_battle_login_get 获取 svr_lvl_rally 数据，
        查找 targetId 匹配且状态为 gathering 的集结。

        Returns:
            (rally_unique_id, rally_pos_encoded) — 失败时返回 ("", "")
        """
        lvl_id = self.client.default_header.get("lvl_id", 0)
        if not lvl_id:
            return "", ""
        try:
            resp = await self.client.lvl_battle_login_get(uid, lvl_id)
            for res in resp.get("res_data", []):
                for push in res.get("push_list", []):
                    for item in push.get("data", []):
                        name = item.get("name", "")
                        raw = item.get("data", "")
                        if "svr_lvl_rally" not in name:
                            continue
                        data = _json.loads(raw) if isinstance(raw, str) else raw
                        for brief in data.get("brief", []):
                            # 匹配目标建筑 + gathering 状态 (0 或 6)
                            if (str(brief.get("targetId", "")) == str(target_id)
                                    and brief.get("status", -1) in (0, 6)):
                                rid = brief.get("uniqueId", "")
                                rpos = str(brief.get("pos", ""))
                                logger.info(
                                    "从 svr_lvl_rally 查到目标 %s 的集结: %s pos=%s",
                                    target_id, rid, rpos,
                                )
                                return rid, rpos
        except Exception as e:
            logger.warning("查询目标集结失败: target=%s err=%s", target_id, e)
        return "", ""

    async def _auto_collect_coal_carts(self, uids: set[int]) -> None:
        """批次执行后自动采集最近的 coal cart (type=10300)

        对每个 uid: 查询 AVA 地图 → 找最近资源车 → 派遣采集。
        失败不影响主流程，仅记录日志。
        """
        lvl_id = self.client.default_header.get("lvl_id", 0)
        if not lvl_id:
            return

        for uid in uids:
            try:
                # 1. 查询 AVA 地图
                resp = await self.client.lvl_battle_login_get(uid, lvl_id)
                code = resp.get("res_header", {}).get("ret_code", -1)
                if code != 0:
                    logger.warning("uid=%d 查询 AVA 地图失败 ret_code=%d", uid, code)
                    continue

                # 2. 解析 briefObjs + user_objs: 提取玩家坐标、10300 资源车、采集队列状态
                player_pos = None
                carts: list[tuple[str, int, int]] = []
                busy_collect = False

                for res in resp.get("res_data", []):
                    for push in res.get("push_list", []):
                        for item in push.get("data", []):
                            name = item.get("name", "")
                            raw = item.get("data", "")
                            try:
                                parsed = _json.loads(raw) if isinstance(raw, str) else raw
                            except (_json.JSONDecodeError, TypeError):
                                continue

                            if "svr_lvl_brief_objs" in name:
                                for obj in parsed.get("briefObjs", parsed.get("briefList", [])):
                                    obj_type = obj.get("type", 0)
                                    raw_pos = obj.get("pos")
                                    if not raw_pos:
                                        continue
                                    ox, oy = decode_pos(int(raw_pos))

                                    if obj_type == 10101:
                                        obj_uid = int(obj.get("uid", 0)) or int(obj.get("id", 0))
                                        if obj_uid == uid:
                                            player_pos = (ox, oy)

                                    elif obj_type == 10300:
                                        cart_id = (
                                            obj.get("uniqueId", "")
                                            or obj.get("unique_id", "")
                                            or f"10300_{obj.get('id', 0)}"
                                        )
                                        carts.append((cart_id, ox, oy))

                            # 检查采集队列: marchType=27 / queueId=6003
                            elif "svr_lvl_user_objs" in name:
                                for obj in parsed.get("objs", []):
                                    march = obj.get("marchBasic", {})
                                    troop_info = obj.get("troopInfo", {})
                                    queue_id = int(troop_info.get("queueId", march.get("queueId", 0)))
                                    march_type = int(march.get("marchType", 0))
                                    if queue_id == 6003 or march_type == 27:
                                        busy_collect = True

                if busy_collect:
                    logger.debug("uid=%d 采集队列已占用 (queueId=6003/marchType=27)，跳过 coal cart", uid)
                    continue

                if not player_pos:
                    logger.warning("uid=%d AVA 地图中未找到玩家坐标，跳过采集", uid)
                    continue
                if not carts:
                    logger.debug("uid=%d AVA 地图中无 coal cart", uid)
                    continue

                # 4. 找最近的 cart
                px, py = player_pos
                nearest = min(carts, key=lambda c: math.hypot(c[1] - px, c[2] - py))
                cart_id, cx, cy = nearest
                dist = math.hypot(cx - px, cy - py)

                # 5. 派遣采集
                collect_resp = await self.client.lvl_collect_cart(uid, lvl_id, cart_id)
                ret = collect_resp.get("res_header", {}).get("ret_code", -1)
                if ret == 0:
                    logger.info(
                        "uid=%d 自动采集 coal cart 成功: cart=%s (%d,%d) 距离=%.1f",
                        uid, cart_id, cx, cy, dist,
                    )
                else:
                    logger.warning(
                        "uid=%d 自动采集 coal cart 失败: cart=%s ret_code=%d%s",
                        uid, cart_id, ret, _lookup_error(ret),
                    )

            except Exception as e:
                logger.warning("uid=%d 自动采集 coal cart 异常: %s", uid, e)

    @staticmethod
    def _extract_rally_id(resp: Dict[str, Any]) -> str:
        """从 create_rally_war 响应中提取 rally_id"""
        try:
            for item in resp["res_data"][0]["push_list"][0]["data"]:
                if "svr_rally_info" in item.get("name", ""):
                    import json as _json
                    data = item.get("data", "")
                    if isinstance(data, str):
                        data = _json.loads(data)
                    return data.get("rally_id", "")
        except (KeyError, IndexError, TypeError):
            pass
        return ""

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    # 通用 action → AVA lvl_ action 映射（当 lvl_id != 0 时自动转换）
    _AVA_ACTION_MAP: Dict[ActionType, ActionType] = {
        ActionType.MOVE_CITY: ActionType.LVL_MOVE_CITY,
        ActionType.ATTACK_TARGET: ActionType.LVL_ATTACK_PLAYER,
        ActionType.SCOUT: ActionType.LVL_SCOUT_PLAYER,
        ActionType.GARRISON_BUILDING: ActionType.LVL_REINFORCE_BUILDING,
        ActionType.INITIATE_RALLY: ActionType.LVL_INITIATE_RALLY,
        ActionType.JOIN_RALLY: ActionType.LVL_JOIN_RALLY,
        ActionType.RETREAT: ActionType.LVL_RECALL_TROOP,
        ActionType.RALLY_DISMISS: ActionType.LVL_RALLY_DISMISS,
        ActionType.RECALL_REINFORCE: ActionType.LVL_RECALL_REINFORCE,
    }

    async def _dispatch(self, instr: AIInstruction, rally_pos: str = "") -> Dict[str, Any]:
        """根据 action 类型分发到对应的 game_api 方法"""
        lvl_id = self.client.default_header.get("lvl_id", 0)

        # AVA 模式：自动将通用 action 映射为 lvl_ 前缀 action
        action = instr.action
        if lvl_id and action in self._AVA_ACTION_MAP:
            original = action
            action = self._AVA_ACTION_MAP[action]
            logger.debug("AVA 模式 action 映射: %s → %s (lvl_id=%s)", original.value, action.value, lvl_id)

        # ATTACK_TARGET 攻击建筑时，AVA 模式需映射为 LVL_ATTACK_BUILDING
        if lvl_id and action == ActionType.LVL_ATTACK_PLAYER and instr.building_id:
            action = ActionType.LVL_ATTACK_BUILDING

        # 集结队列: 发起集结用 6002，参加集结用 6004，solo 行军用 6001
        # 支持 override_queue_id 回退覆盖
        if instr.override_queue_id:
            q_id = instr.override_queue_id
        elif action in self._INITIATE_Q_ACTIONS:
            q_id = 6002
        elif action in self._JOIN_Q_ACTIONS:
            q_id = 6004
        else:
            q_id = 6001
        march = self._build_march_info(instr.uid,
                                         needs_hero=(action not in {ActionType.JOIN_RALLY, ActionType.LVL_JOIN_RALLY}),
                                         queue_id=q_id,
                                         soldier_id=instr.soldier_id, soldier_count=instr.soldier_count)

        if action == ActionType.MOVE_CITY:
            return await self.client.move_city(instr.uid, instr.target_x, instr.target_y)

        elif action == ActionType.ATTACK_TARGET:
            if instr.building_id:
                target_info = {
                    "id": instr.building_id,
                    "pos": str(encode_pos(instr.target_x, instr.target_y)),
                }
                return await self.client.attack_building(instr.uid, target_info, march)
            else:
                return await self.client.attack_player(
                    instr.uid, instr.target_uid, instr.target_x, instr.target_y,
                    march_info=march,
                )

        elif action == ActionType.SCOUT:
            return await self.client.scout_player(
                instr.uid, instr.target_uid, instr.target_x, instr.target_y,
            )

        elif action == ActionType.GARRISON_BUILDING:
            target_info = {
                "id": instr.building_id,
                "pos": str(encode_pos(instr.target_x, instr.target_y)),
            }
            return await self.client.reinforce_building(instr.uid, target_info, march)

        elif action == ActionType.INITIATE_RALLY:
            if instr.building_id:
                target_info = {
                    "id": instr.building_id,
                    "pos": str(encode_pos(instr.target_x, instr.target_y)),
                }
                # 从 building_id 提取 target_type（格式: {type}_{id}_{level}）
                target_type = int(instr.building_id.split("_")[0]) if "_" in instr.building_id else 13
            else:
                target_info = {
                    "id": f"2_{instr.target_uid}_1",
                    "pos": str(encode_pos(instr.target_x, instr.target_y)),
                }
                target_type = 2  # 玩家主城
            return await self.client.create_rally(
                instr.uid, target_info, march, instr.prepare_time,
                target_type=target_type,
            )

        elif action == ActionType.JOIN_RALLY:
            target_info: Dict[str, Any] = {"id": instr.rally_id}
            if rally_pos:
                target_info["pos"] = rally_pos
            return await self.client.join_rally(instr.uid, target_info, march)

        elif action == ActionType.RETREAT:
            return await self.client.recall_troop(instr.uid, instr.troop_ids)

        elif action == ActionType.RALLY_DISMISS:
            return await self.client.rally_dismiss(instr.uid, instr.rally_id)

        elif action == ActionType.RECALL_REINFORCE:
            return await self.client.recall_reinforce(instr.uid, instr.reinforce_id)

        # --- AVA 战场指令 ---
        elif action == ActionType.LVL_MOVE_CITY:
            lvl_id = self.client.default_header.get("lvl_id", 0)
            # 服务器响应含 svr_city_wall push (error=-161)，是城墙状态重置通知，不影响移城成功
            return await self.client.lvl_move_city(instr.uid, instr.target_x, instr.target_y, lvl_id)

        elif action == ActionType.LVL_ATTACK_PLAYER:
            lvl_id = self.client.default_header.get("lvl_id", 0)
            target_id = f"2_{instr.target_uid}_1"
            target_pos = encode_pos(instr.target_x, instr.target_y)
            return await self.client.lvl_attack_player(instr.uid, lvl_id, target_id, target_pos, march)

        elif action == ActionType.LVL_ATTACK_BUILDING:
            lvl_id = self.client.default_header.get("lvl_id", 0)
            target_pos = encode_pos(instr.target_x, instr.target_y)
            # 从 building_id 提取 target_type（格式: {type}_{id}_{...}）
            target_type = int(instr.building_id.split("_")[0]) if "_" in instr.building_id else 10001
            return await self.client.lvl_attack_building(
                instr.uid, lvl_id, instr.building_id, target_pos,
                key=instr.building_key, target_type=target_type, march_info=march,
            )

        elif action == ActionType.LVL_REINFORCE_BUILDING:
            lvl_id = self.client.default_header.get("lvl_id", 0)
            target_type = int(instr.building_id.split("_")[0]) if "_" in instr.building_id else 10006
            return await self.client.lvl_reinforce_building(
                instr.uid, lvl_id, instr.building_id,
                key=instr.building_key, target_type=target_type, march_info=march,
            )

        elif action == ActionType.LVL_SCOUT_PLAYER:
            lvl_id = self.client.default_header.get("lvl_id", 0)
            target_pos = encode_pos(instr.target_x, instr.target_y)
            return await self.client.lvl_scout_player(instr.uid, lvl_id, instr.target_uid, target_pos)

        elif action == ActionType.LVL_SCOUT_BUILDING:
            lvl_id = self.client.default_header.get("lvl_id", 0)
            target_pos = encode_pos(instr.target_x, instr.target_y)
            return await self.client.lvl_scout_building(
                instr.uid, lvl_id, int(instr.building_id) if instr.building_id.isdigit() else 0,
                target_pos, key=instr.building_key,
            )

        elif action == ActionType.LVL_INITIATE_RALLY:
            lvl_id = self.client.default_header.get("lvl_id", 0)
            target_id = f"10101_{instr.target_uid}"
            prepare = instr.prepare_time if instr.prepare_time != 300 else 60
            return await self.client.lvl_create_rally(
                instr.uid, lvl_id, target_id, march, prepare_time=prepare,
            )

        elif action == ActionType.LVL_INITIATE_RALLY_BUILDING:
            lvl_id = self.client.default_header.get("lvl_id", 0)
            prepare = instr.prepare_time if instr.prepare_time != 300 else 60
            return await self.client.lvl_create_rally_building(
                instr.uid, lvl_id, instr.building_id, march, prepare_time=prepare,
            )

        elif action == ActionType.LVL_JOIN_RALLY:
            lvl_id = self.client.default_header.get("lvl_id", 0)
            target_pos = encode_pos(instr.target_x, instr.target_y) if (instr.target_x or instr.target_y) else 0
            if rally_pos:
                target_pos = int(rally_pos)
            return await self.client.lvl_join_rally(instr.uid, lvl_id, instr.rally_id, target_pos, march)

        elif action == ActionType.LVL_RALLY_DISMISS:
            lvl_id = self.client.default_header.get("lvl_id", 0)
            return await self.client.lvl_rally_dismiss(instr.uid, lvl_id, instr.rally_id)

        elif action == ActionType.LVL_RECALL_REINFORCE:
            lvl_id = self.client.default_header.get("lvl_id", 0)
            return await self.client.lvl_recall_reinforce(instr.uid, lvl_id, instr.troop_unique_id)

        elif action == ActionType.LVL_RECALL_TROOP:
            lvl_id = self.client.default_header.get("lvl_id", 0)
            return await self.client.lvl_recall_troop(instr.uid, lvl_id, instr.troop_unique_id)

        elif action == ActionType.LVL_SPEED_UP:
            lvl_id = self.client.default_header.get("lvl_id", 0)
            return await self.client.lvl_speed_up_troop(instr.uid, lvl_id, instr.troop_unique_id)

        elif action == ActionType.LVL_RECALL_FROM_BUILDING:
            lvl_id = self.client.default_header.get("lvl_id", 0)
            pos = encode_pos(instr.target_x, instr.target_y) if (instr.target_x or instr.target_y) else 0
            return await self.client.lvl_recall_from_building(instr.uid, lvl_id, instr.troop_ids, pos)

        else:
            raise ValueError(f"未知 action: {action}")

    @staticmethod
    def _success_message(instr: AIInstruction) -> str:
        """生成人类可读的成功消息"""
        a = instr.action
        if a == ActionType.MOVE_CITY:
            return f"移城到 ({instr.target_x},{instr.target_y})"
        elif a == ActionType.ATTACK_TARGET:
            if instr.building_id:
                return f"攻击建筑 {instr.building_id} @ ({instr.target_x},{instr.target_y})"
            return f"攻击玩家 uid={instr.target_uid} @ ({instr.target_x},{instr.target_y})"
        elif a == ActionType.SCOUT:
            return f"侦察玩家 uid={instr.target_uid} @ ({instr.target_x},{instr.target_y})"
        elif a == ActionType.GARRISON_BUILDING:
            return f"驻防建筑 {instr.building_id} @ ({instr.target_x},{instr.target_y})"
        elif a == ActionType.INITIATE_RALLY:
            target = instr.building_id or f"uid={instr.target_uid}"
            return f"发起集结 → {target} 准备{instr.prepare_time}s"
        elif a == ActionType.JOIN_RALLY:
            return f"加入集结 {instr.rally_id}"
        elif a == ActionType.RETREAT:
            return f"召回部队 {instr.troop_ids}"
        elif a == ActionType.RALLY_DISMISS:
            return f"解散集结 {instr.rally_id}"
        elif a == ActionType.RECALL_REINFORCE:
            return f"撤回增援 {instr.reinforce_id}"
        # --- AVA 战场 ---
        elif a == ActionType.LVL_MOVE_CITY:
            return f"[AVA] 移城到 ({instr.target_x},{instr.target_y})"
        elif a == ActionType.LVL_ATTACK_PLAYER:
            return f"[AVA] 攻击玩家 uid={instr.target_uid} @ ({instr.target_x},{instr.target_y})"
        elif a == ActionType.LVL_ATTACK_BUILDING:
            return f"[AVA] 攻击建筑 {instr.building_id} @ ({instr.target_x},{instr.target_y})"
        elif a == ActionType.LVL_SCOUT_PLAYER:
            return f"[AVA] 侦查玩家 uid={instr.target_uid} @ ({instr.target_x},{instr.target_y})"
        elif a == ActionType.LVL_SCOUT_BUILDING:
            return f"[AVA] 侦查建筑 {instr.building_id} @ ({instr.target_x},{instr.target_y})"
        elif a == ActionType.LVL_INITIATE_RALLY:
            return f"[AVA] 对玩家 uid={instr.target_uid} 发起集结 准备{instr.prepare_time}s"
        elif a == ActionType.LVL_INITIATE_RALLY_BUILDING:
            return f"[AVA] 对建筑 {instr.building_id} 发起集结 准备{instr.prepare_time}s"
        elif a == ActionType.LVL_JOIN_RALLY:
            return f"[AVA] 参与集结 {instr.rally_id}"
        elif a == ActionType.LVL_RALLY_DISMISS:
            return f"[AVA] 解散集结 {instr.rally_id}"
        elif a == ActionType.LVL_RECALL_REINFORCE:
            return f"[AVA] 取消集结 {instr.troop_unique_id}"
        elif a == ActionType.LVL_RECALL_TROOP:
            return f"[AVA] 召回队伍 {instr.troop_unique_id}"
        elif a == ActionType.LVL_SPEED_UP:
            return f"[AVA] 行军加速 {instr.troop_unique_id}"
        elif a == ActionType.LVL_RECALL_FROM_BUILDING:
            return f"[AVA] 从建筑召回 {instr.troop_ids}"
        return ""

    # 默认出征兵力上限（每支部队，测试服实测 5000 可用，10000 被拒）
    DEFAULT_MARCH_SIZE = 5000

    def _build_march_info(self, uid: int, needs_hero: bool = True, queue_id: int = 6001,
                          soldier_id: int = 0, soldier_count: int = 0) -> Dict[str, Any]:
        """根据账号数据自动构建完整 march_info

        服务器要求的完整格式:
            hero, carry_lord, leader, soldier_total_num, heros, queue_id, soldier

        缺少任何字段都会返回 ret_code=30114。

        Args:
            uid: 执行账号 UID
            needs_hero: 是否需要英雄（JOIN_RALLY 队员不需要 leader）
            soldier_id: 手动指定兵种ID（>0 跳过自动选择）
            soldier_count: 手动指定出征数量（>0 使用该值，仍受 DEFAULT_MARCH_SIZE 上限）
        """
        acct = getattr(self, "_accounts", {}).get(uid)
        if not acct:
            return {}

        # 兵种：手动指定 > 自动选数量最多的，限制出征兵力
        sid = str(soldier_id) if soldier_id > 0 else "204"  # 默认弓兵
        cnt = min(soldier_count, self.DEFAULT_MARCH_SIZE) if soldier_count > 0 else self.DEFAULT_MARCH_SIZE
        if soldier_id <= 0 and acct.soldiers:
            best = max(acct.soldiers, key=lambda s: s.value)
            if best.value > 0:
                sid = str(best.id)
                if soldier_count <= 0:
                    cnt = min(best.value, self.DEFAULT_MARCH_SIZE)

        # 英雄：选等级最高的空闲英雄（无英雄数据时用默认 id=21）
        hero_id = 21  # 默认英雄，服务器不校验拥有关系
        if needs_hero and acct.heroes:
            idle = [h for h in acct.heroes if h.state == 0]
            if idle:
                hero_id = max(idle, key=lambda h: h.lv).id

        return {
            "hero": {"main": hero_id, "vice": []},
            "carry_lord": 1,
            "leader": 1 if needs_hero else 0,
            "soldier_total_num": cnt,
            "heros": {},
            "queue_id": queue_id,
            "soldier": {sid: cnt},
            "over_defend": False,
        }

    # --- 建筑尺寸定义（碰撞检测用） ---
    _CITY_TYPES = {2, 10101}       # 玩家主城类型
    _CITY_RADIUS = 2               # 主城: 5x5, 中心 ± 2
    _STEAM_FACTORY_KEY = 10103     # steam factory 模板 key
    _STEAM_FACTORY_RECT = (139, 155, 145, 161)  # 固定矩形 (xmin,ymin,xmax,ymax) inclusive
    _OTHER_BUILDING_WIDTH = 4      # 其余建筑: 4x4, (x,y)-(x+3,y+3)

    # 随机重试参数
    RANDOM_RETRY_COUNT = 3
    RANDOM_RETRY_RADIUS = 15

    # 需要作为障碍物的地图对象类型
    _OBSTACLE_TYPES = {
        2,      # 玩家主城（普通地图）
        10101,  # 玩家主城（AVA）
        27,     # 据点节点
        48,     # 王座
        64,     # 通道建筑
        156,    # 王座侧翼
        8,      # 联盟要塞
        121,    # 联盟旗帜
        10300,  # 资源车
        # AVA 据点/建筑
        10000, 10001, 10002, 10006, 10103, 10104,
    }

    async def _find_empty_spot(
        self, uid: int, target_x: int, target_y: int, max_radius: int = 10,
    ) -> tuple[int, int]:
        """查询地图，在 target 附近找到最近的可移城空位

        算法:
        1. 调用 lvl_get_map_area / get_map_area 获取目标周围地图数据
        2. 提取所有障碍物，按建筑类型计算占地矩形（主城5x5/steam factory固定/其余4x4）
        3. 从 target 开始按切比雪夫距离由近到远搜索第一个不与任何障碍物重叠的位置

        Args:
            uid: 查询用的账号 UID
            target_x, target_y: 期望移城的目标坐标
            max_radius: 最大搜索半径（格）

        Returns:
            (x, y) 最近的空位坐标；找不到时返回原始 target
        """
        # 1. 查询地图
        lvl_id = self.client.default_header.get("lvl_id", 0)
        try:
            if lvl_id:
                map_objs = await self.client.lvl_get_map_area(
                    uid, lvl_id, target_x, target_y, size=3,
                )
            else:
                map_objs = await self.client.get_map_area(
                    uid, target_x, target_y, size=3,
                )
        except Exception as e:
            logger.warning("_find_empty_spot 地图查询失败: %s, 回退原坐标", e)
            return target_x, target_y

        # 2. 提取障碍物占地矩形 (xmin, ymin, xmax, ymax) inclusive
        occupied: list[tuple[int, int, int, int]] = []
        for bid_block in map_objs:
            for obj in bid_block.get("objs", []):
                basic = obj.get("objBasic", obj)
                obj_type = basic.get("type", 0)
                if obj_type not in self._OBSTACLE_TYPES:
                    continue
                obj_key = basic.get("key", 0)
                raw_pos = basic.get("pos")
                if not raw_pos:
                    continue
                ox, oy = decode_pos(int(raw_pos))

                if obj_key == self._STEAM_FACTORY_KEY:
                    rect = self._STEAM_FACTORY_RECT
                elif obj_type in self._CITY_TYPES:
                    # 主城 5x5, pos 是左下角
                    rect = (ox, oy, ox + 4, oy + 4)
                elif obj_type == 10300:
                    # 资源车 1x1
                    rect = (ox, oy, ox, oy)
                else:
                    w = self._OTHER_BUILDING_WIDTH
                    rect = (ox, oy, ox + w - 1, oy + w - 1)
                occupied.append(rect)

        if not occupied:
            logger.info("_find_empty_spot: 目标 (%d,%d) 周围无障碍物", target_x, target_y)
            return target_x, target_y

        logger.info(
            "_find_empty_spot: 目标 (%d,%d) 周围发现 %d 个障碍物",
            target_x, target_y, len(occupied),
        )

        # 3. AABB 碰撞检测：新城 5x5, pos 是左下角
        def is_blocked(x: int, y: int) -> bool:
            nx1, ny1, nx2, ny2 = x, y, x + 4, y + 4
            for bx1, by1, bx2, by2 in occupied:
                if nx1 <= bx2 and nx2 >= bx1 and ny1 <= by2 and ny2 >= by1:
                    return True
            return False

        # 4. 螺旋搜索：按切比雪夫距离从 0 到 max_radius
        #    同一环内按欧氏距离排序，优先选最近的空位
        for r in range(0, max_radius + 1, 2):
            if r == 0:
                candidates = [(target_x, target_y)]
            else:
                candidates = []
                for dx in range(-r, r + 1):
                    for dy in range(-r, r + 1):
                        if max(abs(dx), abs(dy)) == r:
                            candidates.append((target_x + dx, target_y + dy))
                candidates.sort(key=lambda c: (c[0] - target_x) ** 2 + (c[1] - target_y) ** 2)

            for cx, cy in candidates:
                if not (0 <= cx < self.map_width and 0 <= cy < self.map_height):
                    continue
                if not is_blocked(cx, cy):
                    if (cx, cy) != (target_x, target_y):
                        logger.info(
                            "_find_empty_spot: (%d,%d) 被占，选择空位 (%d,%d) 距离=%d",
                            target_x, target_y, cx, cy, r,
                        )
                    return cx, cy

        logger.warning(
            "_find_empty_spot: (%d,%d) 半径 %d 内无空位，回退原坐标",
            target_x, target_y, max_radius,
        )
        return target_x, target_y

    async def _retry_move_city(
        self,
        failed_instr: AIInstruction,
        original_attack_instr: AIInstruction,
    ) -> ExecutionResult:
        """移城失败后重试：1次智能搜索 + 最多3次随机偏移

        Args:
            failed_instr: 已失败的 LVL_MOVE_CITY 指令
            original_attack_instr: 原始 LVL_ATTACK_BUILDING 指令（用于取目标坐标）
        """
        target_x = original_attack_instr.target_x
        target_y = original_attack_instr.target_y
        uid = failed_instr.uid

        # Phase 1: 单次智能搜索
        spot_x, spot_y = await self._find_empty_spot(
            uid, target_x, target_y, max_radius=10,
        )
        retry_instr = failed_instr.model_copy(update={
            "target_x": spot_x,
            "target_y": spot_y,
            "reason": f"移城重试 smart, 智能空位 ({spot_x},{spot_y})",
        })
        logger.info("L0 移城重试 smart: uid=%d → (%d,%d)", uid, spot_x, spot_y)
        result = await self.execute(retry_instr)
        if result.success:
            return result

        # Phase 2: 随机偏移重试
        for attempt in range(1, self.RANDOM_RETRY_COUNT + 1):
            rand_x = target_x + random.randint(
                -self.RANDOM_RETRY_RADIUS, self.RANDOM_RETRY_RADIUS)
            rand_y = target_y + random.randint(
                -self.RANDOM_RETRY_RADIUS, self.RANDOM_RETRY_RADIUS)
            rand_x = max(0, min(rand_x, self.map_width - 1))
            rand_y = max(0, min(rand_y, self.map_height - 1))

            retry_instr = failed_instr.model_copy(update={
                "target_x": rand_x,
                "target_y": rand_y,
                "reason": (
                    f"移城重试 random {attempt}/{self.RANDOM_RETRY_COUNT}, "
                    f"随机偏移 ({rand_x},{rand_y})"
                ),
            })
            logger.info(
                "L0 移城重试 random %d/%d: uid=%d → (%d,%d)",
                attempt, self.RANDOM_RETRY_COUNT, uid, rand_x, rand_y,
            )
            result = await self.execute(retry_instr)
            if result.success:
                return result

        logger.warning(
            "L0 移城重试全部失败: uid=%d, 目标建筑 (%d,%d)",
            uid, target_x, target_y,
        )
        return ExecutionResult(
            success=False, action=ActionType.LVL_MOVE_CITY, uid=uid,
            error=(
                f"移城失败（1次智能+{self.RANDOM_RETRY_COUNT}次随机重试），"
                f"目标建筑附近 ({target_x},{target_y})"
            ),
        )

    # 距离阈值: 超过此格数则先移城再攻打
    MOVE_CITY_DISTANCE_THRESHOLD = 20

    async def _preprocess_lvl_attack_building(
        self, instr: AIInstruction,
    ) -> tuple[AIInstruction | None, str]:
        """LVL_ATTACK_BUILDING 预处理: 部队去重 + 距离检查

        Returns:
            (None, reason)          — 跳过此指令
            (new_instr, "")         — 替换为新指令（可能是 LVL_MOVE_CITY）
            (instr, "")             — 原样放行
        """
        acct = self._accounts.get(instr.uid)
        if not acct:
            return instr, ""

        # 0. 归属预检查: 我方建筑 → ATTACK 转为 REINFORCE
        if instr.building_id and self._buildings and self._my_alliance_id:
            target_bld = self._buildings.get(instr.building_id)
            if target_bld and target_bld.alliance_id == self._my_alliance_id:
                if instr.action == ActionType.LVL_ATTACK_BUILDING:
                    new_instr = instr.model_copy(update={
                        "action": ActionType.LVL_REINFORCE_BUILDING,
                        "reason": f"建筑 {instr.building_id} 已是我方, 转为驻防",
                    })
                    logger.info(
                        "L0 预处理: uid=%d LVL_ATTACK_BUILDING→LVL_REINFORCE_BUILDING "
                        "建筑 %s 已是我方",
                        instr.uid, instr.building_id,
                    )
                    return new_instr, ""
                # LVL_REINFORCE_BUILDING 对我方建筑是正常操作，放行

        # 1. 部队去重: 已有部队正在前往或驻守该建筑
        _active_states = {
            TroopState.MARCHING,
            TroopState.STATIONED,
            TroopState.FIGHTING,
            TroopState.GARRISON,
        }
        for troop in acct.troops:
            if (troop.target_unique_id == instr.building_id
                    and troop.state in _active_states):
                reason = (
                    f"SKIP: uid={instr.uid} 已有部队 {troop.unique_id} "
                    f"(state={troop.state.name}) 前往建筑 {instr.building_id}"
                )
                logger.info("L0 预处理跳过: %s", reason)
                return None, reason

        # 1.5 坐标补全: 缺少坐标时从 buildings 缓存获取
        if (not instr.target_x and not instr.target_y
                and instr.building_id and self._buildings):
            bld = self._buildings.get(instr.building_id)
            if bld and bld.pos != (0, 0):
                instr = instr.model_copy(update={
                    "target_x": bld.pos[0],
                    "target_y": bld.pos[1],
                })
                logger.info(
                    "L0 预处理坐标补全: uid=%d building=%s → (%d,%d)",
                    instr.uid, instr.building_id, bld.pos[0], bld.pos[1],
                )

        # 2. 距离检查: 超过阈值则转换为移城指令
        cx, cy = acct.city_pos
        dx = instr.target_x - cx
        dy = instr.target_y - cy
        dist = math.hypot(dx, dy)

        if dist > self.MOVE_CITY_DISTANCE_THRESHOLD:
            # 安全网: 坐标未解析仍为(0,0)时不转移城，直接放行
            if not instr.target_x and not instr.target_y:
                logger.warning(
                    "L0 预处理: uid=%d building=%s 坐标未解析(0,0), "
                    "跳过移城转换",
                    instr.uid, instr.building_id,
                )
                return instr, ""
            # 智能搜索建筑附近的空位
            move_x, move_y = await self._find_empty_spot(
                instr.uid, instr.target_x, instr.target_y,
            )

            new_instr = instr.model_copy(update={
                "action": ActionType.LVL_MOVE_CITY,
                "target_x": move_x,
                "target_y": move_y,
                "reason": (
                    f"距离={dist:.0f}>{self.MOVE_CITY_DISTANCE_THRESHOLD}, "
                    f"转移城 ({cx},{cy})→({move_x},{move_y}) [智能空位]"
                ),
            })
            logger.info(
                "L0 预处理转换: uid=%d LVL_ATTACK_BUILDING→LVL_MOVE_CITY "
                "dist=%.0f (%d,%d)→(%d,%d) [智能空位]",
                instr.uid, dist, cx, cy, move_x, move_y,
            )
            return new_instr, ""

        # 3. 通过
        return instr, ""

    @staticmethod
    def _extract_rally_info(resp: Dict[str, Any]) -> tuple[str, str]:
        """从 create_rally_war 响应中提取 rally uniqueId 和 pos

        Returns:
            (rally_id, rally_pos_encoded) — 失败时返回 ("", "")

        真实服务器返回 svr_user_objs_inc（type=107 集结对象，含 uniqueId 和 pos）。
        Mock 服务器返回 svr_rally_info（含 rally_id）。
        """
        try:
            for res in resp.get("res_data", []):
                for push in res.get("push_list", []):
                    for item in push.get("data", []):
                        name = item.get("name", "")
                        raw = item.get("data", "")
                        data = _json.loads(raw) if isinstance(raw, str) else raw

                        # Mock: svr_rally_info.rally_id
                        if "svr_rally_info" in name:
                            rid = data.get("rally_id", "")
                            if rid:
                                return rid, ""

                        # 真实: svr_user_objs_inc → type=107 集结对象
                        if "svr_user_objs_inc" in name:
                            for obj in data.get("objs", []):
                                basic = obj.get("objBasic", {})
                                if basic.get("type") == 107:
                                    return (
                                        obj.get("uniqueId", ""),
                                        str(basic.get("pos", "")),
                                    )
        except (KeyError, IndexError, TypeError, _json.JSONDecodeError):
            pass
        return "", ""
