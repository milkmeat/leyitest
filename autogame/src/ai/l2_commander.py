"""L2 军团指挥官 — 全局战略决策引擎

接收 L2GlobalView，调用 LLM 生成战略指令，传给 L1 小队队长。

用法:
    commander = L2Commander(config, llm_client)
    orders = await commander.decide(snapshot)
    # orders: {squad_id: order_text}
"""

from __future__ import annotations

import logging
import os
from typing import Any

from src.ai.llm_client import LLMClient
from src.ai.memory import L2MemoryStore
from src.config.schemas import AppConfig
from src.perception.data_sync import SyncSnapshot
from src.perception.l2_view import L2ViewBuilder

logger = logging.getLogger(__name__)

# prompt 文件目录
_PROMPT_DIR = os.path.join(os.path.dirname(__file__), "prompts")


def _load_prompt(filename: str) -> str:
    """加载 prompt 模板文件"""
    path = os.path.join(_PROMPT_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class L2Commander:
    """L2 军团指挥官 — 一次 decide() 调用生成全局战略指令

    集成 L2MemoryStore，维护最近几轮的战略决策历史，
    为 LLM 提供上下文，提升决策连续性。
    """

    def __init__(self, config: AppConfig, llm_client: LLMClient, memory_max_entries: int = 5):
        self.config = config
        self.llm = llm_client
        self.system_prompt = _load_prompt("l2_system.txt")
        self.view_builder = L2ViewBuilder(config)
        self.memory = L2MemoryStore(max_entries=memory_max_entries)

    async def decide(self, snapshot: SyncSnapshot) -> dict[int, str]:
        """全局决策 → {squad_id: order_text}

        Args:
            snapshot: 当轮同步快照

        Returns:
            {squad_id: 战略指令文本} 字典
        """
        # 1. 构建 L2 全局视图
        view = self.view_builder.build(snapshot)

        # 2. 格式化为 markdown user prompt，附加历史上下文
        user_prompt = self.view_builder.format_text(view)
        history_text = self.memory.format_for_llm(include_loops=3)
        if history_text and "（无历史记录）" not in history_text:
            user_prompt = f"{history_text}\n\n## 当前态势\n\n{user_prompt}"

        # 3. LLM 调用
        response = await self.llm.chat_json(self.system_prompt, user_prompt)

        # 记录 LLM 思考过程
        thinking = response.get("thinking", "")
        if thinking:
            logger.info("L2 thinking: %s", thinking)

        # 4. 解析为 dict[int, str]
        orders = self._parse_orders(response)

        logger.info("L2 决策完成: %d 条指令", len(orders))
        return orders

    def _parse_orders(self, response: dict[str, Any]) -> dict[int, str]:
        """容错解析 LLM JSON → {squad_id: order}

        跳过无效 squad_id，记录缺失小队。
        """
        orders_raw = response.get("orders", [])
        if not isinstance(orders_raw, list):
            logger.warning("L2 响应 orders 不是 list: %s", type(orders_raw))
            return {}

        valid_squad_ids = {s.squad_id for s in self.config.squads.squads}
        result: dict[int, str] = {}

        for i, item in enumerate(orders_raw):
            if not isinstance(item, dict):
                logger.warning("L2 指令 #%d 不是 dict，跳过", i)
                continue

            sid = item.get("squad_id")
            order = item.get("order", "")

            if sid not in valid_squad_ids:
                logger.warning("L2 指令 #%d squad_id=%s 无效，跳过", i, sid)
                continue

            if not order:
                logger.warning("L2 指令 #%d squad_id=%s order 为空，跳过", i, sid)
                continue

            result[sid] = order

        # 记录缺失小队
        missing = valid_squad_ids - result.keys()
        if missing:
            logger.warning("L2 缺失小队指令: %s", missing)

        return result

    def save_history(
        self,
        loop_id: int,
        snapshot: SyncSnapshot,
        l2_orders: dict[int, str],
        instructions: list,
        execution_results: list,
        stats: dict[str, Any] | None = None,
    ):
        """保存当前轮次到历史记录

        Args:
            loop_id: 循环编号
            snapshot: 同步快照
            l2_orders: L2 生成的指令
            instructions: L1 生成的指令列表
            execution_results: L0 执行结果列表
            stats: 循环统计信息（可选）
        """
        from src.ai.memory import LoopHistoryEntry

        entry = LoopHistoryEntry(
            loop_id=loop_id,
            situation_summary="",  # 稍后由 summarizer 填充
            l2_orders=l2_orders,
            l1_instructions=instructions,
            execution_results=execution_results,
            loop_stats=stats or {},
        )
        self.memory.add(entry)
        logger.debug("L2 历史已保存: loop_id=%d", loop_id)

    def get_memory(self) -> L2MemoryStore:
        """获取记忆存储对象，供外部访问或持久化"""
        return self.memory
