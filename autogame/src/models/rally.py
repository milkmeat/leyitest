"""集结数据模型

数据来源:
  - svr_auto_user_rally_info → 集结模式基础信息
  - create_rally_war 命令参数 → 集结创建结构
  - dispatch_troop (march_type=13) → 加入集结结构

注: 测试环境暂无活跃集结样本，模型基于 cmd_config + 需求文档设计，
    后续用实际集结数据校验。
"""

from __future__ import annotations

from enum import IntEnum

from pydantic import BaseModel, Field


class RallyState(IntEnum):
    """集结状态"""
    GATHERING = 0       # 集结中（等待队员加入，5分钟窗口）
    MARCHING = 1        # 行军中
    FIGHTING = 2        # 战斗中
    COMPLETED = 3       # 已结束


class RallyParticipant(BaseModel):
    """集结参与者"""
    uid: int
    troop_unique_id: str = ""
    soldiers: dict[int, int] = Field(default_factory=dict)  # {兵种id: 数量}
    hero_main: int = 0
    hero_vice: int = 0


class Rally(BaseModel):
    """集结

    生命周期: 发起(GATHERING) → 5分钟窗口 → 出发(MARCHING) → 战斗(FIGHTING) → 结束(COMPLETED)
    战斗使用队长的英雄/科技，上限15人加入。
    """
    rally_id: str = ""                     # 集结 unique_id
    leader_uid: int = 0                    # 发起者 UID
    target_unique_id: str = ""             # 目标 unique_id
    target_type: int = 0                   # 目标类型 (2=城市, 13=城寨)
    target_pos: tuple[int, int] = (0, 0)   # 目标坐标

    state: RallyState = RallyState.GATHERING
    prepare_time: int = 300                # 集结准备时长（秒）
    start_time: int = 0                    # 发起时间戳
    march_btime: int = 0                   # 出发时间戳
    march_etime: int = 0                   # 到达时间戳

    participants: list[RallyParticipant] = Field(default_factory=list)
    max_participants: int = 15

    @property
    def participant_count(self) -> int:
        return len(self.participants)

    @property
    def is_full(self) -> bool:
        return self.participant_count >= self.max_participants

    @property
    def participant_uids(self) -> list[int]:
        return [p.uid for p in self.participants]
