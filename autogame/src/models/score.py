"""积分数据模型

数据来源:
  - svr_hurry_up_gs_info → {btime, etime, score} (目前测试环境值全为0)
  - 需求文档中的积分规则:
      · 占领据点持续产分 (score_per_min)
      · 首次占领据点加分 (first_capture_score)
      · 击杀敌方兵力加分

注: 积分计算公式尚待确认（见需求文档 §11），
    模型先覆盖已知字段，后续根据实战数据补充。
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Score(BaseModel):
    """团战积分快照"""
    ally_score: int = 0                    # 我方总积分
    enemy_score: int = 0                   # 敌方总积分
    buildings_held: int = 0                # 当前占据据点数
    kill_count: int = 0                    # 我方击杀兵力数
    enemy_kill_count: int = 0              # 敌方击杀兵力数
    time_remaining: int = 0                # 剩余时间（秒）

    # --- 活动时间窗口 (svr_hurry_up_gs_info) ---
    btime: int = 0                         # 活动开始时间戳
    etime: int = 0                         # 活动结束时间戳

    @property
    def score_diff(self) -> int:
        """分差（正=领先，负=落后）"""
        return self.ally_score - self.enemy_score

    @property
    def is_winning(self) -> bool:
        return self.ally_score > self.enemy_score
