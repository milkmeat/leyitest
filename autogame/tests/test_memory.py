"""记忆模块基础测试

测试 MemoryStore、L2MemoryStore、L1MemoryStore 和 SituationSummarizer 的基本功能。
"""

import pytest

from src.ai.memory import (
    LoopHistoryEntry,
    MemoryStore,
    L2MemoryStore,
    L1MemoryStore,
    SituationSummarizer,
)
from src.executor.l0_executor import AIInstruction, ActionType, ExecutionResult
from src.perception.data_sync import SyncSnapshot


class TestLoopHistoryEntry:
    """LoopHistoryEntry 基础测试"""

    def test_create_empty_entry(self):
        """测试创建空历史条目"""
        entry = LoopHistoryEntry(loop_id=1)
        assert entry.loop_id == 1
        assert entry.situation_summary == ""
        assert entry.l2_orders == {}
        assert entry.l1_instructions == []
        assert entry.execution_results == []

    def test_to_summary_dict(self):
        """测试转换为摘要字典"""
        entry = LoopHistoryEntry(
            loop_id=1,
            situation_summary="我方10人，敌方5人",
            l2_orders={1: "进攻东部", 2: "防守西部"},
            l1_instructions=[
                AIInstruction(action=ActionType.SCOUT, uid=100, target_uid=200),
                AIInstruction(action=ActionType.ATTACK_TARGET, uid=101, target_uid=201),
            ],
            execution_results=[
                ExecutionResult(success=True, action=ActionType.SCOUT, uid=100),
                ExecutionResult(success=False, action=ActionType.ATTACK_TARGET, uid=101),
            ],
        )
        summary = entry.to_summary_dict()
        assert summary["loop_id"] == 1
        assert summary["situation"] == "我方10人，敌方5人"
        assert summary["l2_orders"] == {1: "进攻东部", 2: "防守西部"}
        assert "SCOUT×1" in summary["l1_actions"]
        assert "ATTACK_TARGET×1" in summary["l1_actions"]
        assert summary["results"]["total"] == 2
        assert summary["results"]["success"] == 1
        assert summary["results"]["failed"] == 1


class TestMemoryStore:
    """MemoryStore 基础测试"""

    def test_add_and_retrieve(self):
        """测试添加和获取历史记录"""
        store = MemoryStore(max_entries=3)

        # 添加 3 条记录
        for i in range(1, 4):
            store.add(LoopHistoryEntry(loop_id=i))

        assert len(store) == 3
        assert store.get_latest().loop_id == 3

        # 获取最近 2 条
        recent = store.get_recent(count=2)
        assert len(recent) == 2
        assert recent[0].loop_id == 2
        assert recent[1].loop_id == 3

    def test_max_entries_limit(self):
        """测试最大条目限制（环形缓冲）"""
        store = MemoryStore(max_entries=2)

        # 添加 4 条记录，只保留最后 2 条
        for i in range(1, 5):
            store.add(LoopHistoryEntry(loop_id=i))

        assert len(store) == 2
        latest = store.get_latest()
        assert latest.loop_id == 4

        recent = store.get_recent()
        assert recent[0].loop_id == 3
        assert recent[1].loop_id == 4

    def test_clear(self):
        """测试清空历史"""
        store = MemoryStore(max_entries=5)
        store.add(LoopHistoryEntry(loop_id=1))
        assert len(store) == 1

        store.clear()
        assert len(store) == 0
        assert store.get_latest() is None


class TestL2MemoryStore:
    """L2MemoryStore 测试"""

    def test_format_for_llm_empty(self):
        """测试格式化空历史"""
        store = L2MemoryStore(max_entries=5)
        text = store.format_for_llm(include_loops=3)
        assert "（无历史记录）" in text

    def test_format_for_llm_with_data(self):
        """测试格式化有数据的历史"""
        store = L2MemoryStore(max_entries=5)
        store.add(LoopHistoryEntry(
            loop_id=1,
            situation_summary="第一轮",
            l2_orders={1: "进攻"},
        ))
        store.add(LoopHistoryEntry(
            loop_id=2,
            situation_summary="第二轮",
            l2_orders={1: "防守"},
        ))

        text = store.format_for_llm(include_loops=2)
        assert "Loop #1" in text
        assert "Loop #2" in text
        assert "第一轮" in text
        assert "第二轮" in text
        assert "小队 1" in text


class TestL1MemoryStore:
    """L1MemoryStore 测试"""

    def test_filter_squad_instructions(self):
        """测试过滤小队指令"""
        store = L1MemoryStore(squad_id=1, max_entries=5)
        squad_uids = {100, 101, 102}

        all_instructions = [
            AIInstruction(action=ActionType.SCOUT, uid=100, target_uid=200),
            AIInstruction(action=ActionType.ATTACK_TARGET, uid=101, target_uid=201),
            AIInstruction(action=ActionType.SCOUT, uid=103, target_uid=202),  # 不属于本小队
        ]

        filtered = store.filter_squad_instructions(all_instructions, squad_uids)
        assert len(filtered) == 2
        assert all(instr.uid in squad_uids for instr in filtered)

    def test_filter_squad_results(self):
        """测试过滤小队执行结果"""
        store = L1MemoryStore(squad_id=1, max_entries=5)
        squad_uids = {100, 101, 102}

        all_results = [
            ExecutionResult(success=True, action=ActionType.SCOUT, uid=100),
            ExecutionResult(success=True, action=ActionType.ATTACK_TARGET, uid=101),
            ExecutionResult(success=True, action=ActionType.SCOUT, uid=103),  # 不属于本小队
        ]

        filtered = store.filter_squad_results(all_results, squad_uids)
        assert len(filtered) == 2
        assert all(r.uid in squad_uids for r in filtered)

    def test_format_for_llm(self):
        """测试格式化 L1 历史"""
        store = L1MemoryStore(squad_id=5, max_entries=5)
        store.add(LoopHistoryEntry(
            loop_id=1,
            situation_summary="小队5第一轮",
            l1_instructions=[
                AIInstruction(action=ActionType.SCOUT, uid=100, target_uid=200),
            ],
        ))

        text = store.format_for_llm(include_loops=1)
        assert "小队 5 历史记录" in text
        assert "Loop #1" in text
        assert "小队5第一轮" in text


class TestSituationSummarizer:
    """SituationSummarizer 测试"""

    def test_build_system_prompt(self):
        """测试系统 prompt 构建"""
        prompt = SituationSummarizer._build_system_prompt()
        assert "SLG 游戏战况分析师" in prompt
        assert "200 tokens" in prompt

    @pytest.mark.asyncio
    async def test_fallback_summary(self):
        """测试兜底摘要生成"""
        snapshot = SyncSnapshot(
            accounts={},
            buildings=[],
            enemies=[],
            loop_id=1,
        )

        # 创建一个假的 summarizer（不调用 LLM）
        summary = SituationSummarizer._fallback_summary(snapshot, None)
        assert "我方0人" in summary

    def test_build_user_prompt(self):
        """测试用户 prompt 构建"""
        summarizer = SituationSummarizer(llm_client=None)  # client=None for testing

        snapshot = SyncSnapshot(
            accounts={},
            buildings=[],
            enemies=[],
            loop_id=1,
        )

        prompt = summarizer._build_user_prompt(
            snapshot=snapshot,
            l2_orders={1: "进攻东部"},
            stats={"actions_ok": 5, "actions_fail": 1},
        )

        assert "当前战况数据" in prompt
        assert "进攻东部" in prompt
        assert "成功: 5" in prompt
        assert "失败: 1" in prompt
