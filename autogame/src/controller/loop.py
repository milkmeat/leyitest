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
import os
import signal
import time
from dataclasses import asdict, dataclass, field
from typing import Any

from src.config.schemas import AppConfig
from src.executor.game_api import GameAPIClient
from src.executor.l0_executor import L0Executor
from src.perception.data_sync import DataSyncer


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

    def __init__(self, config: AppConfig, client: GameAPIClient):
        self.config = config
        self.client = client
        self.syncer = DataSyncer(client, config)
        self.executor = L0Executor(client, config)
        self.interval = config.system.loop.interval_seconds
        self.log_dir = config.system.logging.dir
        self._stop = False

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

        # ── Phase 2: L2 (stub) ──
        t0 = time.monotonic()
        l2_orders: list[Any] = []
        try:
            # TODO: 接入 L2Commander
            l2_orders = []
        except Exception as e:
            stats.phase_errors.append(f"l2: {e}")
        stats.l2_time = round(time.monotonic() - t0, 2)
        print(f"[L2]     stub — 跳过 ({stats.l2_time:.2f}s)")

        # ── Phase 3: L1 (stub) ──
        t0 = time.monotonic()
        instructions: list[Any] = []
        try:
            # TODO: 接入 L1Leader (10 个并行)
            instructions = []
        except Exception as e:
            stats.phase_errors.append(f"l1: {e}")
        stats.l1_time = round(time.monotonic() - t0, 2)
        print(f"[L1]     stub — 跳过 ({stats.l1_time:.2f}s)")

        # ── Phase 4: Action ──
        t0 = time.monotonic()
        stats.instructions_count = len(instructions)
        if instructions:
            try:
                results = await self.executor.execute_batch(instructions)
                stats.actions_ok = sum(1 for r in results if r.success)
                stats.actions_fail = sum(1 for r in results if not r.success)
            except Exception as e:
                stats.phase_errors.append(f"action: {e}")
        stats.action_time = round(time.monotonic() - t0, 2)
        print(f"[action] {stats.instructions_count} 条指令 ({stats.action_time:.2f}s)")

        stats.total_time = round(time.monotonic() - round_start, 2)
        return stats

    def _write_log(self, stats: LoopStats):
        """将 LoopStats 序列化为 JSON 写入 logs/ 目录"""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            path = os.path.join(self.log_dir, f"loop_{stats.loop_id}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(asdict(stats), f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # 日志写入失败不影响主循环
