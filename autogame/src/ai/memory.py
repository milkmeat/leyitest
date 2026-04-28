"""上下文管理（记忆模块）

- 保留最近5个loop的历史（可配置）
- 每条历史: 态势摘要 + 下达的指令 + 执行结果
- 压缩策略: 由LLM生成摘要（非硬编码），每条不超过200 tokens
- L2和L1各自维护独立历史
"""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from src.executor.l0_executor import AIInstruction, ExecutionResult, ActionType
from src.perception.data_sync import SyncSnapshot

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# 数据模型
# ------------------------------------------------------------------

@dataclass
class LoopHistoryEntry:
    """单轮历史记录

    记录一轮循环的完整上下文：
    - loop_id: 循环编号
    - situation_summary: 态势摘要（由 LLM 生成）
    - l2_orders: L2 指令（仅 L2 记忆使用）
    - l1_instructions: L1 生成的指令列表
    - execution_results: L0 执行结果
    - loop_stats: 循环统计信息（用于生成摘要）
    """
    loop_id: int
    situation_summary: str = ""
    l2_orders: dict[int, str] = field(default_factory=dict)
    l1_instructions: list[AIInstruction] = field(default_factory=list)
    execution_results: list[ExecutionResult] = field(default_factory=list)
    loop_stats: dict[str, Any] = field(default_factory=dict)

    def to_summary_dict(self) -> dict[str, Any]:
        """转换为摘要格式，用于 LLM prompt"""
        return {
            "loop_id": self.loop_id,
            "situation": self.situation_summary,
            "l2_orders": self.l2_orders,
            "l1_actions": self._summarize_actions(),
            "results": self._summarize_results(),
        }

    def _summarize_actions(self) -> list[str]:
        """简要描述 L1 指令"""
        if not self.l1_instructions:
            return []
        # 按动作类型分组统计
        action_counts: dict[ActionType, int] = {}
        for instr in self.l1_instructions:
            action_counts[instr.action] = action_counts.get(instr.action, 0) + 1
        # 生成简短描述
        summaries = []
        for action, count in action_counts.items():
            summaries.append(f"{action.value}×{count}")
        return summaries

    def _summarize_results(self) -> dict[str, int]:
        """简要描述执行结果"""
        return {
            "total": len(self.execution_results),
            "success": sum(1 for r in self.execution_results if r.success),
            "failed": sum(1 for r in self.execution_results if not r.success),
        }


class MemoryStore:
    """记忆存储基类

    管理 LoopHistoryEntry 的环形缓冲区，提供历史查询和压缩功能。
    """

    def __init__(self, max_entries: int = 5):
        self.max_entries = max_entries
        self._history: deque[LoopHistoryEntry] = deque(maxlen=max_entries)

    def add(self, entry: LoopHistoryEntry):
        """添加新的历史记录"""
        self._history.append(entry)
        logger.debug("记忆添加: loop_id=%d (当前容量 %d/%d)",
                     entry.loop_id, len(self._history), self.max_entries)

    def get_recent(self, count: int = 0) -> list[LoopHistoryEntry]:
        """获取最近的历史记录

        Args:
            count: 返回数量，0 表示返回全部

        Returns:
            历史记录列表，从旧到新排序
        """
        if count <= 0:
            return list(self._history)
        return list(self._history)[-count:]

    def get_latest(self) -> LoopHistoryEntry | None:
        """获取最新的历史记录"""
        return self._history[-1] if self._history else None

    def clear(self):
        """清空历史"""
        self._history.clear()
        logger.info("记忆已清空")

    def __len__(self) -> int:
        return len(self._history)


class L2MemoryStore(MemoryStore):
    """L2 军团指挥官的记忆

    存储全局战略级别的历史，包括：
    - 每轮的全局态势摘要
    - L2 下达的指令
    - 执行结果的宏观统计
    """

    def format_for_llm(self, include_loops: int = 3) -> str:
        """格式化历史为 LLM 可读文本

        Args:
            include_loops: 包含最近几轮历史

        Returns:
            Markdown 格式的历史描述
        """
        recent = self.get_recent(count=include_loops)
        if not recent:
            return "（无历史记录）"

        lines = ["## 历史记录", ""]
        for entry in recent:
            lines.append(f"### Loop #{entry.loop_id}")
            lines.append(f"**态势**: {entry.situation_summary or '(未生成摘要)'}")

            if entry.l2_orders:
                lines.append("**L2 指令**:")
                for squad_id, order in entry.l2_orders.items():
                    lines.append(f"  - 小队 {squad_id}: {order}")

            results = entry._summarize_results()
            if results["total"] > 0:
                lines.append(
                    f"**执行结果**: 成功 {results['success']}/{results['total']}"
                )
            lines.append("")

        return "\n".join(lines)


class L1MemoryStore(MemoryStore):
    """L1 小队队长的记忆

    存储战术级别的历史，按小队 ID 分组存储：
    - 每轮小队局部态势
    - L1 生成的具体指令
    - L0 执行结果
    """

    def __init__(self, squad_id: int, max_entries: int = 5):
        super().__init__(max_entries)
        self.squad_id = squad_id

    def filter_squad_instructions(
        self,
        all_instructions: list[AIInstruction],
        squad_uids: set[int],
    ) -> list[AIInstruction]:
        """从全局指令列表中过滤出属于本小队的指令

        Args:
            all_instructions: L1 层生成的全部指令
            squad_uids: 本小队的 UID 集合

        Returns:
            属于本小队的指令列表
        """
        return [instr for instr in all_instructions if instr.uid in squad_uids]

    def filter_squad_results(
        self,
        all_results: list[ExecutionResult],
        squad_uids: set[int],
    ) -> list[ExecutionResult]:
        """从全局执行结果中过滤出属于本小队的结果

        Args:
            all_results: L0 层的全部执行结果
            squad_uids: 本小队的 UID 集合

        Returns:
            属于本小队的执行结果列表
        """
        return [r for r in all_results if r.uid in squad_uids]

    def format_for_llm(self, include_loops: int = 3) -> str:
        """格式化历史为 LLM 可读文本

        Args:
            include_loops: 包含最近几轮历史

        Returns:
            Markdown 格式的小队历史描述
        """
        recent = self.get_recent(count=include_loops)
        if not recent:
            return f"（小队 {self.squad_id} 无历史记录）"

        lines = [f"## 小队 {self.squad_id} 历史记录", ""]
        for entry in recent:
            lines.append(f"### Loop #{entry.loop_id}")
            lines.append(f"**态势**: {entry.situation_summary or '(未生成摘要)'}")

            if entry.l1_instructions:
                lines.append("**本小队行动**:")
                for instr in entry.l1_instructions:
                    desc = instr.reason
                    if not desc:
                        if instr.building_id:
                            desc = f"building={instr.building_id}"
                        elif instr.target_uid:
                            desc = f"target={instr.target_uid}"
                        elif instr.target_x or instr.target_y:
                            desc = f"({instr.target_x},{instr.target_y})"
                        else:
                            desc = str(instr.uid)
                    lines.append(f"  - {instr.action.value}: {desc}")
            else:
                lines.append("**本小队行动**: (无行动)")

            results = entry._summarize_results()
            if results["total"] > 0:
                lines.append(
                    f"**执行结果**: 成功 {results['success']}/{results['total']}"
                )
            lines.append("")

        return "\n".join(lines)


# ------------------------------------------------------------------
# 摘要生成器（使用 LLM 压缩历史）
# ------------------------------------------------------------------

class SituationSummarizer:
    """态势摘要生成器

    使用 LLM 将详细的 SyncSnapshot 和 LoopStats
    压缩为简短的态势描述（不超过 200 tokens）。
    """

    def __init__(self, llm_client):
        from src.ai.llm_client import LLMClient
        self.llm: LLMClient = llm_client
        self._system_prompt = self._build_system_prompt()

    @staticmethod
    def _build_system_prompt() -> str:
        return """你是一个 SLG 游戏战况分析师。请将当前战况压缩为一段简洁的中文摘要。

要求：
1. 控制在 200 tokens 以内
2. 重点突出：敌我力量对比、关键建筑争夺、伤亡情况
3. 使用简洁的军事术语
4. 不要提及具体 UID，用"我方/敌方"替代

输出格式：JSON 对象，例如 {"summary": "我方50人集结北部据点，敌方30人防守中..."}"""

    async def summarize(
        self,
        snapshot: SyncSnapshot,
        l2_orders: dict[int, str] | None = None,
        stats: dict[str, Any] | None = None,
    ) -> str:
        """生成态势摘要

        Args:
            snapshot: 当前同步快照
            l2_orders: L2 指令（可选）
            stats: 循环统计信息（可选）

        Returns:
            态势摘要文本
        """
        user_prompt = self._build_user_prompt(snapshot, l2_orders, stats)

        try:
            response = await self.llm.chat_json(
                self._system_prompt,
                user_prompt,
                temperature=0.3,  # 低温度保证稳定性
            )
            summary = response.get("summary", "")
            if not summary:
                # 兜底：返回简化描述
                summary = self._fallback_summary(snapshot, stats)
            return summary
        except Exception as e:
            logger.warning("LLM 摘要生成失败: %s，使用兜底方案", e)
            return self._fallback_summary(snapshot, stats)

    def _build_user_prompt(
        self,
        snapshot: SyncSnapshot,
        l2_orders: dict[int, str] | None,
        stats: dict[str, Any] | None,
    ) -> str:
        """构建用户提示词"""
        lines = ["当前战况数据：", ""]

        # 账号统计
        lines.append(f"我方账号: {len(snapshot.accounts)} 个")
        if snapshot.errors:
            lines.append(f"同步失败: {len(snapshot.errors)} 个")

        # 建筑统计
        buildings = snapshot.buildings
        if buildings:
            lines.append(f"地图建筑: {len(buildings)} 个")
            # 按类型分组
            by_type: dict[int, int] = {}
            for b in buildings:
                by_type[b.obj_type] = by_type.get(b.obj_type, 0) + 1
            for btype, count in sorted(by_type.items()):
                lines.append(f"  - 类型 {btype}: {count} 个")

        # 敌方统计
        enemies = snapshot.enemies
        if enemies:
            lines.append(f"敌方玩家: {len(enemies)} 个")

        # L2 指令（如果有）
        if l2_orders:
            lines.append("")
            lines.append("本轮 L2 战略指令:")
            for squad_id, order in l2_orders.items():
                lines.append(f"  - 小队 {squad_id}: {order}")

        # 执行结果（如果有）
        if stats:
            lines.append("")
            lines.append("执行统计:")
            lines.append(f"  - 指令数: {stats.get('instructions_count', 0)}")
            lines.append(f"  - 成功: {stats.get('actions_ok', 0)}")
            lines.append(f"  - 失败: {stats.get('actions_fail', 0)}")

        return "\n".join(lines)

    @staticmethod
    def _fallback_summary(
        snapshot: SyncSnapshot,
        stats: dict[str, Any] | None = None,
    ) -> str:
        """兜底摘要（LLM 失败时使用）"""
        parts = []
        parts.append(f"我方{len(snapshot.accounts)}人")

        if snapshot.buildings:
            parts.append(f"地图{len(snapshot.buildings)}建筑")

        if snapshot.enemies:
            parts.append(f"敌方{len(snapshot.enemies)}人")

        if stats and stats.get("actions_ok", 0) > 0:
            parts.append(f"执行{stats['actions_ok']}成功")

        if stats and stats.get("actions_fail", 0) > 0:
            parts.append(f"{stats['actions_fail']}失败")

        return "，".join(parts) + "。"
