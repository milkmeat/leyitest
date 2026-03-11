"""L1 小队队长 — 战术决策引擎

单小队: L1Leader — 构建视图 → 调用 LLM → 解析指令
多小队: L1Coordinator — 并行调用所有 L1Leader，异常隔离

用法:
    leader = L1Leader(config, llm_client, squad)
    instructions = await leader.decide(snapshot, l2_order="进攻东部")

    coordinator = L1Coordinator(config, llm_client)
    all_instructions = await coordinator.decide_all(snapshot, l2_orders={})
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from src.ai.llm_client import LLMClient
from src.config.schemas import AppConfig, SquadEntry
from src.executor.l0_executor import AIInstruction, ActionType
from src.perception.data_sync import SyncSnapshot
from src.perception.l1_view import L1ViewBuilder

logger = logging.getLogger(__name__)

# 加载 L1 system prompt
_PROMPT_DIR = os.path.join(os.path.dirname(__file__), "prompts")


def _load_system_prompt() -> str:
    path = os.path.join(_PROMPT_DIR, "l1_system.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class L1Leader:
    """单小队 L1 队长 — 一次 decide() 调用生成该小队的全部指令"""

    def __init__(
        self,
        config: AppConfig,
        llm_client: LLMClient,
        squad: SquadEntry,
    ):
        self.config = config
        self.llm = llm_client
        self.squad = squad
        self.view_builder = L1ViewBuilder(config)
        self._system_prompt = _load_system_prompt()

    async def decide(
        self,
        snapshot: SyncSnapshot,
        l2_order: str = "",
    ) -> list[AIInstruction]:
        """生成本小队的行动指令

        Args:
            snapshot: 当轮同步快照
            l2_order: L2 战略指令

        Returns:
            AIInstruction 列表（可能为空）
        """
        # 1. 构建局部视图
        view = self.view_builder.build(snapshot, self.squad, l2_order)

        # 2. 生成 user prompt
        user_prompt = self.view_builder.format_text(view)

        # 3. 调用 LLM
        response = await self.llm.chat_json(
            self._system_prompt, user_prompt
        )

        # 4. 解析响应
        instructions = self._parse_response(response)

        logger.info(
            "L1 squad=%d (%s): %d 条指令",
            self.squad.squad_id, self.squad.name, len(instructions),
        )
        return instructions

    def _parse_response(self, response: dict[str, Any]) -> list[AIInstruction]:
        """容错解析 LLM JSON 响应为 AIInstruction 列表

        跳过无效项，校验 UID 属于本小队。
        """
        raw_instructions = response.get("instructions", [])
        if not isinstance(raw_instructions, list):
            logger.warning("L1 响应 instructions 不是 list: %s", type(raw_instructions))
            return []

        valid_uids = set(self.squad.member_uids)
        results: list[AIInstruction] = []

        for i, item in enumerate(raw_instructions):
            if not isinstance(item, dict):
                logger.warning("L1 指令 #%d 不是 dict，跳过", i)
                continue

            # 校验 UID 属于本小队
            uid = item.get("uid", 0)
            if uid and uid not in valid_uids:
                logger.warning(
                    "L1 指令 #%d uid=%s 不属于小队 %d，跳过",
                    i, uid, self.squad.squad_id,
                )
                continue

            try:
                instr = AIInstruction.model_validate(item)
                results.append(instr)
            except Exception as e:
                logger.warning("L1 指令 #%d 解析失败: %s — %s", i, e, item)
                continue

        return results


class L1Coordinator:
    """L1 并行协调器 — 管理所有小队的 L1Leader"""

    def __init__(self, config: AppConfig, llm_client: LLMClient):
        self.config = config
        self.llm = llm_client
        self.leaders: dict[int, L1Leader] = {}

        for squad in config.squads.squads:
            self.leaders[squad.squad_id] = L1Leader(config, llm_client, squad)

    async def decide_all(
        self,
        snapshot: SyncSnapshot,
        l2_orders: dict[int, str] | None = None,
    ) -> list[AIInstruction]:
        """并行调用所有 L1Leader，汇总指令

        Args:
            snapshot: 当轮同步快照
            l2_orders: {squad_id: order_text}，可选

        Returns:
            所有小队的 AIInstruction 合并列表
        """
        if l2_orders is None:
            l2_orders = {}

        tasks = []
        squad_ids = []
        for sid, leader in self.leaders.items():
            order = l2_orders.get(sid, "")
            tasks.append(leader.decide(snapshot, l2_order=order))
            squad_ids.append(sid)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_instructions: list[AIInstruction] = []
        for sid, result in zip(squad_ids, results):
            if isinstance(result, Exception):
                logger.error("L1 squad=%d 决策失败: %s", sid, result)
            elif isinstance(result, list):
                all_instructions.extend(result)

        logger.info("L1 总计 %d 条指令 (来自 %d 个小队)", len(all_instructions), len(self.leaders))
        return all_instructions
