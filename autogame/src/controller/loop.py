"""AIController 主循环 — 60 秒一轮的 5 阶段编排

阶段:
  1. Sync   — 并发同步所有账号 + 地图数据
  2. L2     — 军团指挥官战略决策 (当前 stub)
  3. L1     — 小队队长战术决策 (当前 stub)
  4. Action — L0 执行器批量发送命令
  5. Sleep  — 等待下一轮

用法:
  controller = AIController(config, client)
  await controller.run(max_rounds=3)        # 跑 3 轮退出
  await controller.run()                    # 无限循环
"""

import asyncio
import json
import logging
import os
import signal
import time
from dataclasses import asdict, dataclass, field
from typing import Any

from src.config.schemas import AppConfig
from src.executor.game_api import GameAPIClient
from src.executor.l0_executor import L0Executor
from src.perception.data_sync import DataSyncer

logger = logging.getLogger(__name__)

# 条件导入 — llm_client 可选
try:
    from src.ai.llm_client import LLMClient
    from src.ai.l1_leader import L1Coordinator
    from src.ai.l2_commander import L2Commander
    from src.ai.memory import SituationSummarizer
except ImportError:
    LLMClient = None  # type: ignore[misc,assignment]
    L1Coordinator = None  # type: ignore[misc,assignment]
    L2Commander = None  # type: ignore[misc,assignment]
    SituationSummarizer = None  # type: ignore[misc,assignment]


@dataclass
class LoopStats:
    """单轮统计数据"""
    loop_id: int = 0
    sync_time: float = 0.0
    l2_time: float = 0.0
    l1_time: float = 0.0
    action_time: float = 0.0
    total_time: float = 0.0
    account_count: int = 0
    building_count: int = 0
    enemy_count: int = 0
    error_count: int = 0
    instructions_count: int = 0
    actions_ok: int = 0
    actions_fail: int = 0
    phase_errors: list[str] = field(default_factory=list)


class AIController:
    """主循环控制器 — 串联 Sync → L2 → L1 → Action → Sleep"""

    def __init__(self, config: AppConfig, client: GameAPIClient, llm_client=None,
                 mock_l2: str | None = None, l1_prompt: str | None = None):
        self.config = config
        self.client = client
        self.syncer = DataSyncer(client, config)
        self.executor = L0Executor(client, config)
        self.interval = config.system.loop.interval_seconds
        self.log_dir = config.system.logging.dir
        self._stop = False
        self.mock_l2 = mock_l2  # Mock L2 指令（跳过 L2 LLM 调用）
        self.l1_prompt = l1_prompt  # L1 prompt 模板名称

        # L2 指挥官 + L1 协调器 + 摘要生成器（可选 — 传入 llm_client 时启用 AI 决策）
        self.l2_commander = None
        self.l1_coordinator = None
        self.summarizer = None
        if llm_client is not None and L1Coordinator is not None:
            self.l1_coordinator = L1Coordinator(config, llm_client, prompt_template=l1_prompt)
        if llm_client is not None and L2Commander is not None:
            self.l2_commander = L2Commander(config, llm_client)
        if llm_client is not None and SituationSummarizer is not None:
            self.summarizer = SituationSummarizer(llm_client)

    async def run(self, max_rounds: int = 0):
        """启动主循环

        Args:
            max_rounds: 最大轮数，0 表示无限循环
        """
        # 注册 SIGINT 优雅退出
        loop = asyncio.get_running_loop()
        original_handler = signal.getsignal(signal.SIGINT)

        def _on_sigint():
            print("\n[ctrl+c] 正在优雅退出...")
            self._stop = True

        try:
            loop.add_signal_handler(signal.SIGINT, _on_sigint)
        except NotImplementedError:
            # Windows 不支持 add_signal_handler
            pass

        print(f"AIController 启动 (间隔={self.interval}s, "
              f"轮数={'无限' if max_rounds == 0 else max_rounds})")

        loop_id = 0
        try:
            while not self._stop:
                loop_id += 1
                if max_rounds > 0 and loop_id > max_rounds:
                    break

                try:
                    stats = await self._run_one_loop(loop_id)
                except Exception as e:
                    print(f"[loop #{loop_id}] 异常: {e}")
                    continue

                self._write_log(stats)

                # 判断是否需要继续
                if self._stop:
                    break
                if max_rounds > 0 and loop_id >= max_rounds:
                    break

                # Sleep 阶段
                remaining = self.interval - stats.total_time
                if remaining > 0:
                    print(f"[loop #{loop_id}] 完成 ({stats.total_time:.2f}s) "
                          f"— 等待 {remaining:.2f}s")
                    try:
                        await asyncio.sleep(remaining)
                    except asyncio.CancelledError:
                        break
                else:
                    print(f"[loop #{loop_id}] 完成 ({stats.total_time:.2f}s) "
                          f"— 超时，立即进入下一轮")
        finally:
            try:
                loop.remove_signal_handler(signal.SIGINT)
            except (NotImplementedError, ValueError):
                pass
            signal.signal(signal.SIGINT, original_handler)
            print(f"AIController 停止 (共 {loop_id} 轮)")

    async def _run_one_loop(self, loop_id: int) -> LoopStats:
        """执行一轮完整的 5 阶段流程"""
        stats = LoopStats(loop_id=loop_id)
        round_start = time.monotonic()
        print(f"[loop #{loop_id}] 开始")

        # ── Phase 1: Sync ──
        t0 = time.monotonic()
        snapshot = None
        try:
            snapshot = await self.syncer.sync(loop_id=loop_id)
            stats.account_count = len(snapshot.accounts)
            stats.building_count = len(snapshot.buildings)
            stats.enemy_count = len(snapshot.enemies)
            stats.error_count = len(snapshot.errors)
        except Exception as e:
            stats.phase_errors.append(f"sync: {e}")
        stats.sync_time = round(time.monotonic() - t0, 2)
        print(f"[sync]   {stats.account_count} 账号, {stats.building_count} 建筑, "
              f"{stats.enemy_count} 敌方 ({stats.sync_time:.2f}s)")

        # ── Phase 2: L2 ──
        t0 = time.monotonic()
        l2_orders: dict[int, str] = {}
        try:
            if self.mock_l2:
                # Mock 模式：解析固定指令，跳过 LLM 调用
                l2_orders = self._parse_mock_l2(self.mock_l2)
                print(f"[L2]     Mock 模式: {self.mock_l2[:50]}...")
            elif self.l2_commander and snapshot:
                l2_orders = await self.l2_commander.decide(snapshot)
        except Exception as e:
            stats.phase_errors.append(f"l2: {e}")
        stats.l2_time = round(time.monotonic() - t0, 2)
        if self.mock_l2 or self.l2_commander:
            print(f"[L2]     {len(l2_orders)} 条指令 ({stats.l2_time:.2f}s)")
        else:
            print(f"[L2]     跳过 (无 LLM) ({stats.l2_time:.2f}s)")

        # ── Phase 3: L1 ──
        t0 = time.monotonic()
        instructions: list[Any] = []
        try:
            if self.l1_coordinator and snapshot:
                instructions = await self.l1_coordinator.decide_all(snapshot, l2_orders=l2_orders)
        except Exception as e:
            stats.phase_errors.append(f"l1: {e}")
        stats.l1_time = round(time.monotonic() - t0, 2)
        if self.l1_coordinator:
            print(f"[L1]     {len(instructions)} 条指令 ({stats.l1_time:.2f}s)")
        else:
            print(f"[L1]     跳过 (无 LLM) ({stats.l1_time:.2f}s)")

        # ── Phase 4: Action ──
        t0 = time.monotonic()
        stats.instructions_count = len(instructions)
        results: list[Any] = []
        if instructions:
            try:
                results = await self.executor.execute_batch(
                    instructions, accounts=snapshot.accounts if snapshot else None,
                )
                stats.actions_ok = sum(1 for r in results if r.success)
                stats.actions_fail = sum(1 for r in results if not r.success)
            except Exception as e:
                stats.phase_errors.append(f"action: {e}")
        stats.action_time = round(time.monotonic() - t0, 2)
        print(f"[action] {stats.instructions_count} 条指令 ({stats.action_time:.2f}s)")

        # ── Phase 4.5: 验收日志（测试模式） ──
        if snapshot:
            self._print_acceptance_log(snapshot, l2_orders)

        # ── Phase 5: Memory (可选) ──
        # 在有 AI 决策且有 snapshot 时，保存历史记录并生成摘要
        if snapshot and (self.l2_commander or self.l1_coordinator):
            await self._save_memory(
                loop_id, snapshot, l2_orders, instructions, results, stats,
            )

        stats.total_time = round(time.monotonic() - round_start, 2)
        return stats

    async def _save_memory(
        self,
        loop_id: int,
        snapshot,
        l2_orders: dict[int, str],
        instructions: list,
        results: list,
        stats: LoopStats,
    ):
        """保存历史记录到 L2 和 L1 记忆

        Args:
            loop_id: 循环编号
            snapshot: 同步快照
            l2_orders: L2 指令
            instructions: L1 指令
            results: L0 执行结果
            stats: 循环统计
        """
        try:
            # 生成态势摘要
            situation_summary = ""
            if self.summarizer:
                situation_summary = await self.summarizer.summarize(
                    snapshot, l2_orders, asdict(stats),
                )

            # 保存 L2 历史
            if self.l2_commander:
                self.l2_commander.save_history(
                    loop_id=loop_id,
                    snapshot=snapshot,
                    l2_orders=l2_orders,
                    instructions=instructions,
                    execution_results=results,
                    stats=asdict(stats),
                )
                # 更新摘要
                latest = self.l2_commander.memory.get_latest()
                if latest:
                    latest.situation_summary = situation_summary

            # 保存 L1 历史（所有小队）
            if self.l1_coordinator:
                self.l1_coordinator.save_all_history(
                    loop_id=loop_id,
                    all_instructions=instructions,
                    all_results=results,
                    stats=asdict(stats),
                )
                # 更新摘要
                for leader in self.l1_coordinator.leaders.values():
                    latest = leader.memory.get_latest()
                    if latest:
                        latest.situation_summary = situation_summary

            logger.info("记忆已保存: loop_id=%d, 摘要=%s", loop_id,
                       situation_summary[:50] if situation_summary else "(无)")

        except Exception as e:
            logger.warning("保存记忆失败: %s", e)

    def _parse_mock_l2(self, mock_instruction: str) -> dict[int, str]:
        """解析 mock L2 指令为 {squad_id: order_text} 字典

        支持的格式:
        1. "[小队 1 (Alpha)] 控制 建筑 pos:( 154, 170 )" -> {1: "控制 建筑 pos:( 154, 170 )"}
        2. "squad_1: 控制 建筑 pos:( 154, 170 )" -> {1: "控制 建筑 pos:( 154, 170 )"}
        3. 直接传给所有小队的通用指令

        Returns:
            {squad_id: order_text} 字典
        """
        import re

        # 尝试解析 "[小队 N (Name)]" 格式
        pattern = r'\[小队\s+(\d+)\s*\([^)]*\)\]\s*(.+)'
        match = re.search(pattern, mock_instruction)
        if match:
            squad_id = int(match.group(1))
            order = match.group(2).strip()
            return {squad_id: order}

        # 尝试解析 "squad_N:" 格式
        pattern = r'squad_(\d+)\s*:\s*(.+)'
        match = re.search(pattern, mock_instruction, re.IGNORECASE)
        if match:
            squad_id = int(match.group(1))
            order = match.group(2).strip()
            return {squad_id: order}

        # 默认：将指令应用到所有小队
        valid_squad_ids = {s.squad_id for s in self.config.squads.squads}
        return {sid: mock_instruction.strip() for sid in valid_squad_ids}

    def _print_acceptance_log(self, snapshot, l2_orders: dict[int, str]):
        """Print acceptance log: member positions + building control status

        Print each loop:
        1. All squad members' current positions
        2. Target building control status
        3. Alert when building controlled by our alliance
        """
        from src.perception.l1_view import parse_target_coordinates, find_building_by_pos

        print(f"[Accept] ---")

        # 1. Print all member positions
        print(f"[Accept] Member Positions:")
        for uid, acct in snapshot.accounts.items():
            total_soldiers = sum(s.value for s in acct.soldiers)
            troop_count = len([t for t in acct.troops if t.state.name != "IDLE"])
            print(f"[Accept]   uid={uid} ({acct.city_pos[0]},{acct.city_pos[1]}) "
                  f"soldiers={total_soldiers} dispatched={troop_count}")

        # 2. Parse target building and print control status
        target_building = None
        my_alliance_id = self.config.squads.active_alliance.aid

        # Parse target coordinates from L2 order
        for squad_id, order in l2_orders.items():
            target_pos = parse_target_coordinates(order)
            if target_pos:
                target_building = find_building_by_pos(snapshot.buildings, target_pos)
                break

        if target_building:
            # Print target building control status
            owner = "Neutral" if target_building.alliance_id == 0 else f"Alliance{target_building.alliance_id}"
            print(f"[Accept]   Target Building: {target_building.unique_id} "
                  f"({target_building.pos[0]},{target_building.pos[1]}) "
                  f"owner={owner}")

            # Check if controlled by our alliance
            if target_building.alliance_id == my_alliance_id:
                print(f"[Accept]   *** BUILDING CONTROLLED BY OUR ALLIANCE ***")
        else:
            # Target not found, print nearby buildings
            if snapshot.buildings:
                print(f"[Accept]   Nearby Buildings (top 5):")
                for b in snapshot.buildings[:5]:
                    owner = "Neutral" if b.alliance_id == 0 else f"Alliance{b.alliance_id}"
                    print(f"[Accept]     {b.unique_id} ({b.pos[0]},{b.pos[1]}) owner={owner}")
            else:
                print(f"[Accept]   (no building data)")

        print(f"[Accept] ---")

    def _write_log(self, stats: LoopStats):
        """将 LoopStats 序列化为 JSON 写入 logs/ 目录"""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            path = os.path.join(self.log_dir, f"loop_{stats.loop_id}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(asdict(stats), f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # 日志写入失败不影响主循环
