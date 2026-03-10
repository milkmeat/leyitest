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

import logging
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel

from src.executor.game_api import GameAPIClient
from src.config.schemas import AppConfig
from src.utils.coords import encode_pos

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# AI 指令数据结构（L1 LLM 输出 JSON 直接反序列化）
# ------------------------------------------------------------------

class ActionType(str, Enum):
    MOVE_CITY = "MOVE_CITY"
    ATTACK_TARGET = "ATTACK_TARGET"
    SCOUT = "SCOUT"
    GARRISON_BUILDING = "GARRISON_BUILDING"
    INITIATE_RALLY = "INITIATE_RALLY"
    JOIN_RALLY = "JOIN_RALLY"
    RETREAT = "RETREAT"


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
    rally_id: str = ""                 # 集结 ID（JOIN_RALLY）
    troop_ids: list[str] = []          # 部队 ID 列表（RETREAT）
    prepare_time: int = 300            # 集结准备时间秒（INITIATE_RALLY）
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

        return True, ""

    async def execute(self, instr: AIInstruction) -> ExecutionResult:
        """校验 → 翻译 → 调用 game_api → 返回结果"""
        # 1. 校验
        ok, err_msg = self.validate(instr)
        if not ok:
            logger.warning("L0 校验失败: %s — %s", instr.action.value, err_msg)
            return ExecutionResult(
                success=False, action=instr.action, uid=instr.uid, error=err_msg,
            )

        # 2. 执行
        try:
            resp = await self._dispatch(instr)
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
                logger.warning("L0 服务器返回错误: %s uid=%s — %s", instr.action.value, instr.uid, err)
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

    async def execute_batch(self, instructions: list[AIInstruction]) -> list[ExecutionResult]:
        """顺序执行一批指令（不并发，避免同一账号竞态）"""
        results = []
        for instr in instructions:
            result = await self.execute(instr)
            results.append(result)
        return results

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    async def _dispatch(self, instr: AIInstruction) -> Dict[str, Any]:
        """根据 action 类型分发到对应的 game_api 方法"""
        action = instr.action

        if action == ActionType.MOVE_CITY:
            return await self.client.move_city(instr.uid, instr.target_x, instr.target_y)

        elif action == ActionType.ATTACK_TARGET:
            if instr.building_id:
                # 攻击建筑
                target_info = {
                    "id": instr.building_id,
                    "pos": str(encode_pos(instr.target_x, instr.target_y)),
                }
                return await self.client.attack_building(instr.uid, target_info, {})
            else:
                # 攻击玩家
                return await self.client.attack_player(
                    instr.uid, instr.target_uid, instr.target_x, instr.target_y,
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
            return await self.client.reinforce_building(instr.uid, target_info, {})

        elif action == ActionType.INITIATE_RALLY:
            # 集结目标: 优先用 building_id，否则用 target_uid
            if instr.building_id:
                target_info = {
                    "id": instr.building_id,
                    "pos": str(encode_pos(instr.target_x, instr.target_y)),
                }
            else:
                target_info = {
                    "id": f"2_{instr.target_uid}_1",
                    "pos": str(encode_pos(instr.target_x, instr.target_y)),
                }
            return await self.client.create_rally(
                instr.uid, target_info, {}, instr.prepare_time,
            )

        elif action == ActionType.JOIN_RALLY:
            target_info = {"id": instr.rally_id}
            return await self.client.join_rally(instr.uid, target_info, {})

        elif action == ActionType.RETREAT:
            return await self.client.recall_troop(instr.uid, instr.troop_ids)

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
        return ""
