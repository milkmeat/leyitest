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
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel

from src.executor.game_api import GameAPIClient
from src.config.schemas import AppConfig
from src.models.player_state import PlayerState
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
    RALLY_DISMISS = "RALLY_DISMISS"
    RECALL_REINFORCE = "RECALL_REINFORCE"


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
    reinforce_id: str = ""             # 增援部队 unique_id（RECALL_REINFORCE 用）
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

        elif instr.action == ActionType.RALLY_DISMISS:
            if not instr.rally_id:
                return False, "RALLY_DISMISS 需要 rally_id 非空"

        elif instr.action == ActionType.RECALL_REINFORCE:
            if not instr.reinforce_id:
                return False, "RECALL_REINFORCE 需要 reinforce_id 非空"

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

    async def execute_batch(
        self,
        instructions: list[AIInstruction],
        accounts: Optional[dict[int, PlayerState]] = None,
    ) -> list[ExecutionResult]:
        """顺序执行一批指令（不并发，避免同一账号竞态）

        支持：
        - 自动构建 march_info（从 accounts 获取兵力/英雄数据）
        - 同循环 Rally：INITIATE_RALLY 成功后自动提取 rally_id，
          回填到后续 rally_id 为空的 JOIN_RALLY 指令
        """
        self._accounts = accounts or {}
        results = []
        # 最近一次成功的 rally 信息（同循环回填用）
        last_rally_id: str = ""
        last_rally_pos: str = ""

        for instr in instructions:
            # 自动回填 rally_id 和坐标
            if (instr.action == ActionType.JOIN_RALLY
                    and not instr.rally_id and last_rally_id):
                instr = instr.model_copy(update={"rally_id": last_rally_id})
                logger.info("自动回填 rally_id=%s → uid=%d", last_rally_id, instr.uid)

            result = await self.execute(instr, rally_pos=last_rally_pos)
            results.append(result)

            # 从 INITIATE_RALLY 响应中提取 rally_id 和 pos
            if (result.success and instr.action == ActionType.INITIATE_RALLY):
                rid, rpos = self._extract_rally_info(result.server_response)
                if rid:
                    last_rally_id = rid
                    last_rally_pos = rpos
                    logger.info("提取 rally_id=%s pos=%s from INITIATE_RALLY uid=%d", rid, rpos, instr.uid)

        return results

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

    async def _dispatch(self, instr: AIInstruction, rally_pos: str = "") -> Dict[str, Any]:
        """根据 action 类型分发到对应的 game_api 方法"""
        action = instr.action
        march = self._build_march_info(instr.uid, needs_hero=(action != ActionType.JOIN_RALLY))

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
            else:
                target_info = {
                    "id": f"2_{instr.target_uid}_1",
                    "pos": str(encode_pos(instr.target_x, instr.target_y)),
                }
            return await self.client.create_rally(
                instr.uid, target_info, march, instr.prepare_time,
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
        return ""

    # 默认出征兵力上限（每支部队，测试服实测 5000 可用，10000 被拒）
    DEFAULT_MARCH_SIZE = 5000

    def _build_march_info(self, uid: int, needs_hero: bool = True) -> Dict[str, Any]:
        """根据账号数据自动构建完整 march_info

        服务器要求的完整格式:
            hero, carry_lord, leader, soldier_total_num, heros, queue_id, soldier

        缺少任何字段都会返回 ret_code=30114。

        Args:
            uid: 执行账号 UID
            needs_hero: 是否需要英雄（JOIN_RALLY 队员不需要 leader）
        """
        acct = getattr(self, "_accounts", {}).get(uid)
        if not acct:
            return {}

        # 兵种：选数量最多的，限制出征兵力
        soldier_id = "204"  # 默认弓兵
        soldier_count = self.DEFAULT_MARCH_SIZE
        if acct.soldiers:
            best = max(acct.soldiers, key=lambda s: s.value)
            if best.value > 0:
                soldier_id = str(best.id)
                soldier_count = min(best.value, self.DEFAULT_MARCH_SIZE)

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
            "soldier_total_num": soldier_count,
            "heros": {},
            "queue_id": 6001,
            "soldier": {soldier_id: soldier_count},
            "over_defend": False,
        }

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
