"""L1 Squad Leader - Tactical Decision Engine

Single squad: L1Leader — build view → call LLM → parse instructions
Multi squad: L1Coordinator — parallel all L1Leader with exception isolation

Usage:
    leader = L1Leader(config, llm_client, squad)
    instructions = await leader.decide(snapshot, l2_order="attack east")

    coordinator = L1Coordinator(config, llm_client)
    all_instructions = await coordinator.decide_all(snapshot, l2_orders={})
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from src.ai.llm_client import LLMClient
from src.ai.memory import L1MemoryStore
from src.config.schemas import AppConfig, SquadEntry
from src.executor.l0_executor import AIInstruction, ActionType
from src.perception.data_sync import SyncSnapshot
from src.perception.l1_view import L1ViewBuilder

logger = logging.getLogger(__name__)

# 加载 L1 system prompt
_PROMPT_DIR = os.path.join(os.path.dirname(__file__), "prompts")


def _load_system_prompt(template_name: str | None = None) -> str:
    """加载 L1 system prompt 模板

    Args:
        template_name: 模板名称，如 "ava"、"ava_test"。默认使用 "l1_system.txt"
    """
    if template_name:
        # 查找 l1_system_{template_name}.txt
        filename = f"l1_system_{template_name}.txt"
    else:
        filename = "l1_system.txt"

    path = os.path.join(_PROMPT_DIR, filename)
    logger.info(f"Loading L1 prompt template: {filename} (template_name={template_name})")
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.info(f"L1 prompt loaded successfully: {len(content)} chars")
        return content
    except FileNotFoundError:
        logger.warning(f"Prompt template {filename} not found, using default")
        # 回退到默认模板
        default_path = os.path.join(_PROMPT_DIR, "l1_system.txt")
        with open(default_path, "r", encoding="utf-8") as f:
            return f.read()


class L1Leader:
    """Single Squad L1 Leader - decide() call generates all instructions for this squad

    Integrates L1MemoryStore, maintains squad-level tactical decision history.
    """

    def __init__(
        self,
        config: AppConfig,
        llm_client: LLMClient,
        squad: SquadEntry,
        memory_max_entries: int = 5,
        prompt_template: str | None = None,
    ):
        self.config = config
        self.llm = llm_client
        self.squad = squad
        self.view_builder = L1ViewBuilder(config)
        self._prompt_template = prompt_template  # Save template name for logging
        self._system_prompt = _load_system_prompt(prompt_template)
        self.memory = L1MemoryStore(
            squad_id=squad.squad_id,
            max_entries=memory_max_entries,
        )

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

        # 2. 生成 user prompt，附加历史上下文
        user_prompt = self.view_builder.format_text(view)
        history_text = self.memory.format_for_llm(include_loops=3)
        if history_text and "（小队" not in history_text:
            user_prompt = f"{history_text}\n\n## 当前态势\n\n{user_prompt}"

        # 3. 调用 LLM
        context = f"L1 squad={self.squad.squad_id} ({self.squad.name})"
        response = await self.llm.chat_json(
            self._system_prompt, user_prompt, context=context
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

    def save_history(
        self,
        loop_id: int,
        squad_instructions: list[AIInstruction],
        all_results: list,
        stats: dict[str, Any] | None = None,
    ):
        """保存当前轮次到小队历史记录

        Args:
            loop_id: 循环编号
            squad_instructions: 本小队的指令列表
            all_results: 全部执行结果（会被过滤为仅本小队）
            stats: 循环统计信息（可选）
        """
        from src.ai.memory import LoopHistoryEntry

        squad_uids = set(self.squad.member_uids)
        squad_results = self.memory.filter_squad_results(all_results, squad_uids)

        entry = LoopHistoryEntry(
            loop_id=loop_id,
            situation_summary="",  # 稍后由 summarizer 填充
            l2_orders={},  # L1 不需要 L2 指令
            l1_instructions=squad_instructions,
            execution_results=squad_results,
            loop_stats=stats or {},
        )
        self.memory.add(entry)
        logger.debug("L1 squad=%d 历史已保存: loop_id=%d", self.squad.squad_id, loop_id)

    def get_memory(self) -> L1MemoryStore:
        """获取记忆存储对象，供外部访问或持久化"""
        return self.memory


class L1Coordinator:
    """L1 并行协调器 — 管理所有小队的 L1Leader"""

    def __init__(self, config: AppConfig, llm_client: LLMClient,
                 prompt_template: str | None = None):
        self.config = config
        self.llm = llm_client
        self.leaders: dict[int, L1Leader] = {}

        for squad in config.squads.squads:
            self.leaders[squad.squad_id] = L1Leader(
                config, llm_client, squad,
                prompt_template=prompt_template,
            )

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
        # 如果 l2_orders 非空，只处理有指令的小队（用于 mock 测试场景）
        target_leaders = (
            {sid: self.leaders[sid] for sid in l2_orders if sid in self.leaders}
            if l2_orders
            else self.leaders
        )
        for sid, leader in target_leaders.items():
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

    def save_all_history(
        self,
        loop_id: int,
        all_instructions: list[AIInstruction],
        all_results: list,
        stats: dict[str, Any] | None = None,
    ):
        """批量保存所有小队的历史记录

        Args:
            loop_id: 循环编号
            all_instructions: 全部指令列表
            all_results: 全部执行结果
            stats: 循环统计信息（可选）
        """
        for sid, leader in self.leaders.items():
            squad_uids = set(leader.squad.member_uids)
            squad_instructions = [
                instr for instr in all_instructions if instr.uid in squad_uids
            ]
            leader.save_history(loop_id, squad_instructions, all_results, stats)
        logger.debug("L1 全部小队历史已保存: loop_id=%d", loop_id)

    def get_all_memories(self) -> dict[int, L1MemoryStore]:
        """获取所有小队的记忆存储对象"""
        return {sid: leader.get_memory() for sid, leader in self.leaders.items()}
