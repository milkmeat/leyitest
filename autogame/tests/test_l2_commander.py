"""L2 Commander 单元测试

覆盖:
- 正常 LLM 返回解析
- 缺失小队 warning
- 非法 squad_id 跳过
- 空 response (dry_run 兼容)
- thinking 字段日志记录
"""

import logging
from unittest.mock import AsyncMock, patch

import pytest

from src.ai.l2_commander import L2Commander
from src.config.schemas import (
    AccountEntry,
    AccountsConfig,
    ActivityConfig,
    AllianceInfo,
    AlliancesConfig,
    AllianceSquadGroup,
    AppConfig,
    SquadEntry,
    SquadsConfig,
    SystemConfig,
)
from src.models.enemy import Enemy
from src.models.player_state import PlayerState, Soldier
from src.perception.data_sync import SyncSnapshot


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture()
def config_2squads() -> AppConfig:
    """2 小队、10 账号的最小配置"""
    return AppConfig(
        accounts=AccountsConfig(
            accounts=[AccountEntry(uid=i, name=f"p{i}") for i in range(1, 11)],
            alliances=AlliancesConfig(
                ours=AllianceInfo(aid=100, name="Ours"),
                enemy=AllianceInfo(aid=200, name="Enemy"),
            ),
        ),
        squads=SquadsConfig(alliances={"ours": AllianceSquadGroup(
            aid=100, name="Ours", squads=[
                SquadEntry(squad_id=1, name="Alpha", leader_uid=1, member_uids=[1, 2, 3, 4, 5]),
                SquadEntry(squad_id=2, name="Bravo", leader_uid=6, member_uids=[6, 7, 8, 9, 10]),
            ],
        )}),
        activity=ActivityConfig(),
        system=SystemConfig(),
    )


def _make_account(uid: int, x: int = 100, y: int = 200) -> PlayerState:
    return PlayerState(
        uid=uid,
        name=f"p{uid}",
        city_pos=(x, y),
        power=10000,
        soldiers=[Soldier(id=101, value=1000)],
        troops=[],
    )


def _make_snapshot(accounts: dict[int, PlayerState] | None = None) -> SyncSnapshot:
    return SyncSnapshot(
        accounts=accounts or {},
        enemies=[],
        buildings=[],
        loop_id=1,
    )


def _mock_llm_client(response: dict):
    """创建 mock LLMClient，chat_json 返回指定 response"""
    client = AsyncMock()
    client.chat_json = AsyncMock(return_value=response)
    return client


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

class TestL2Commander:
    @pytest.mark.asyncio
    async def test_decide_normal(self, config_2squads: AppConfig):
        """正常 LLM 返回含 orders，验证 dict 解析正确"""
        llm_response = {
            "thinking": "分析态势后决定进攻",
            "orders": [
                {"squad_id": 1, "order": "进攻东部区域", "priority": "high"},
                {"squad_id": 2, "order": "防守据点", "priority": "medium"},
            ],
        }
        llm = _mock_llm_client(llm_response)
        accounts = {i: _make_account(i) for i in range(1, 11)}
        snapshot = _make_snapshot(accounts=accounts)

        commander = L2Commander(config_2squads, llm)
        orders = await commander.decide(snapshot)

        assert orders == {1: "进攻东部区域", 2: "防守据点"}
        llm.chat_json.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_parse_missing_squad(self, config_2squads: AppConfig, caplog):
        """缺失某个小队，记录 warning，其余正常"""
        llm_response = {
            "orders": [
                {"squad_id": 1, "order": "进攻", "priority": "high"},
                # squad 2 缺失
            ],
        }
        llm = _mock_llm_client(llm_response)
        accounts = {i: _make_account(i) for i in range(1, 11)}
        snapshot = _make_snapshot(accounts=accounts)

        commander = L2Commander(config_2squads, llm)
        with caplog.at_level(logging.WARNING):
            orders = await commander.decide(snapshot)

        assert orders == {1: "进攻"}
        assert "缺失小队指令" in caplog.text

    @pytest.mark.asyncio
    async def test_parse_invalid_squad_id(self, config_2squads: AppConfig, caplog):
        """非法 squad_id 被跳过"""
        llm_response = {
            "orders": [
                {"squad_id": 1, "order": "进攻", "priority": "high"},
                {"squad_id": 999, "order": "无效小队", "priority": "low"},
                {"squad_id": 2, "order": "防守", "priority": "medium"},
            ],
        }
        llm = _mock_llm_client(llm_response)
        accounts = {i: _make_account(i) for i in range(1, 11)}
        snapshot = _make_snapshot(accounts=accounts)

        commander = L2Commander(config_2squads, llm)
        with caplog.at_level(logging.WARNING):
            orders = await commander.decide(snapshot)

        assert orders == {1: "进攻", 2: "防守"}
        assert "squad_id=999 无效" in caplog.text

    @pytest.mark.asyncio
    async def test_parse_empty_response(self, config_2squads: AppConfig):
        """空 response（如 dry_run）返回空 dict"""
        # dry_run 的 _DRY_RUN_RESPONSE 没有 orders 字段
        llm_response = {
            "thinking": "dry_run 模式",
            "instructions": [{"action": "SCOUT"}],
        }
        llm = _mock_llm_client(llm_response)
        accounts = {i: _make_account(i) for i in range(1, 11)}
        snapshot = _make_snapshot(accounts=accounts)

        commander = L2Commander(config_2squads, llm)
        orders = await commander.decide(snapshot)

        assert orders == {}

    @pytest.mark.asyncio
    async def test_decide_logs_thinking(self, config_2squads: AppConfig, caplog):
        """验证 LLM 返回的 thinking 字段被记录到日志"""
        llm_response = {
            "thinking": "敌方集中在东部，应全力进攻",
            "orders": [
                {"squad_id": 1, "order": "进攻东部", "priority": "high"},
                {"squad_id": 2, "order": "支援东部", "priority": "high"},
            ],
        }
        llm = _mock_llm_client(llm_response)
        accounts = {i: _make_account(i) for i in range(1, 11)}
        snapshot = _make_snapshot(accounts=accounts)

        commander = L2Commander(config_2squads, llm)
        with caplog.at_level(logging.INFO):
            await commander.decide(snapshot)

        assert "敌方集中在东部" in caplog.text
