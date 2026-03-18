"""Pydantic v2 配置数据模型

定义 YAML 配置文件对应的 Pydantic schema，用于加载时自动校验。

配置文件 → Schema 映射:
  accounts.yaml  → AccountsConfig
  squads.yaml    → SquadsConfig
  activity.yaml  → ActivityConfig
  system.yaml    → SystemConfig
  (聚合)         → AppConfig
"""

from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr, model_validator


# ------------------------------------------------------------------
# accounts.yaml
# ------------------------------------------------------------------

class AccountEntry(BaseModel):
    """单个账号条目 — 只存标识，运行时信息从服务器同步"""
    uid: int
    name: str = ""


class ReserveEntry(BaseModel):
    """备用账号条目"""
    uid: int


class AllianceInfo(BaseModel):
    """联盟元信息"""
    aid: int
    name: str = ""


class AlliancesConfig(BaseModel):
    """联盟配置 — 我方 + 对手方"""
    ours: AllianceInfo
    enemy: AllianceInfo


class AccountsConfig(BaseModel):
    """accounts.yaml 顶层"""
    accounts: list[AccountEntry]
    enemies: list[AccountEntry] = Field(default_factory=list)
    reserves: list[ReserveEntry] = Field(default_factory=list)
    alliances: AlliancesConfig | None = None

    @model_validator(mode="after")
    def check_unique_uids(self) -> AccountsConfig:
        all_uids = (
            [a.uid for a in self.accounts]
            + [e.uid for e in self.enemies]
            + [r.uid for r in self.reserves]
        )
        if len(all_uids) != len(set(all_uids)):
            seen: set[int] = set()
            dupes = [u for u in all_uids if u in seen or seen.add(u)]  # type: ignore[func-returns-value]
            raise ValueError(f"账号 UID 重复: {dupes}")
        return self

    def all_uids(self) -> set[int]:
        """返回所有我方账号 UID（含备用，不含 enemies）"""
        return {a.uid for a in self.accounts} | {r.uid for r in self.reserves}

    def active_uids(self) -> list[int]:
        """返回活跃账号 UID 列表（不含备用）"""
        return [a.uid for a in self.accounts]

    def enemy_uids(self) -> list[int]:
        """返回对手方 UID 列表"""
        return [e.uid for e in self.enemies]


# ------------------------------------------------------------------
# squads.yaml
# ------------------------------------------------------------------

class SquadEntry(BaseModel):
    """单个小队"""
    squad_id: int
    name: str = ""
    leader_uid: int
    member_uids: list[int]

    @model_validator(mode="after")
    def check_leader_in_members(self) -> SquadEntry:
        if self.leader_uid not in self.member_uids:
            raise ValueError(
                f"小队 {self.squad_id} 队长 {self.leader_uid} 不在成员列表中"
            )
        return self


class AllianceSquadGroup(BaseModel):
    """单联盟的小队配置"""
    aid: int
    name: str = ""
    squads: list[SquadEntry] = Field(default_factory=list)


class SquadsConfig(BaseModel):
    """squads.yaml 顶层 — 多联盟结构

    通过 alliances dict 管理多个联盟的小队，_active_key 选择当前运行联盟。
    .squads 属性向后兼容，返回当前活跃联盟的小队列表。
    """
    alliances: dict[str, AllianceSquadGroup]
    _active_key: str = PrivateAttr(default="ours")

    @property
    def squads(self) -> list[SquadEntry]:
        """向后兼容: 返回当前活跃联盟的小队列表"""
        return self.alliances[self._active_key].squads

    @property
    def active_alliance(self) -> AllianceSquadGroup:
        return self.alliances[self._active_key]

    def set_active(self, key: str):
        if key not in self.alliances:
            raise ValueError(f"未知联盟: {key}")
        self._active_key = key

    def all_squad_uids(self) -> set[int]:
        """返回所有联盟中小队成员的 UID 集合"""
        uids: set[int] = set()
        for group in self.alliances.values():
            for sq in group.squads:
                uids.update(sq.member_uids)
        return uids

    @model_validator(mode="after")
    def check_no_duplicate_members(self) -> SquadsConfig:
        """校验: 同一联盟内不可有重复成员（跨联盟允许）"""
        for key, group in self.alliances.items():
            seen: set[int] = set()
            for sq in group.squads:
                for uid in sq.member_uids:
                    if uid in seen:
                        raise ValueError(
                            f"联盟 {key} 中 UID {uid} 出现在多个小队中"
                        )
                    seen.add(uid)
        return self


# ------------------------------------------------------------------
# activity.yaml
# ------------------------------------------------------------------

class MapConfig(BaseModel):
    width: int = 1000
    height: int = 1000


class MarchConfig(BaseModel):
    speed: int = 2                      # 秒/格
    max_distance: int = 999


class RallyConfig(BaseModel):
    window_seconds: int = 300
    max_members: int = 15


class CombatConfig(BaseModel):
    counter_bonus: float = 1.3
    counter_penalty: float = 0.7


class ScoringConfig(BaseModel):
    kill_point: int = 1
    building_capture_point: int = 100
    building_hold_point_per_min: int = 10


class ActivityConfig(BaseModel):
    """activity.yaml 顶层"""
    duration_seconds: int = 7200
    map: MapConfig = Field(default_factory=MapConfig)
    march: MarchConfig = Field(default_factory=MarchConfig)
    rally: RallyConfig = Field(default_factory=RallyConfig)
    combat: CombatConfig = Field(default_factory=CombatConfig)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)


# ------------------------------------------------------------------
# system.yaml
# ------------------------------------------------------------------

class LoopConfig(BaseModel):
    interval_seconds: int = 60
    sync_timeout: int = 5


class LLMConfig(BaseModel):
    timeout_seconds: int = 30
    max_retries: int = 1
    model: str = ""
    base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    api_key: str = ""  # 空串时从 ZHIPU_API_KEY 环境变量读取


class ConcurrencyConfig(BaseModel):
    max_api_concurrent: int = 20
    max_llm_concurrent: int = 10


class LoggingConfig(BaseModel):
    level: str = "INFO"
    dir: str = "logs"


class SystemConfig(BaseModel):
    """system.yaml 顶层"""
    loop: LoopConfig = Field(default_factory=LoopConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    concurrency: ConcurrencyConfig = Field(default_factory=ConcurrencyConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


# ------------------------------------------------------------------
# 聚合顶层
# ------------------------------------------------------------------

class AppConfig(BaseModel):
    """全部配置聚合 — 传入主循环的唯一配置对象"""
    accounts: AccountsConfig
    squads: SquadsConfig
    activity: ActivityConfig
    system: SystemConfig

    def all_known_uids(self) -> set[int]:
        """返回所有已知 UID（accounts + enemies + reserves）"""
        return (
            self.accounts.all_uids()
            | {e.uid for e in self.accounts.enemies}
        )

    @model_validator(mode="after")
    def check_squad_uids_in_accounts(self) -> AppConfig:
        """校验: 所有联盟小队成员 UID 必须存在于 accounts/enemies 中"""
        valid_uids = self.all_known_uids()
        for key, group in self.squads.alliances.items():
            for sq in group.squads:
                for uid in sq.member_uids:
                    if uid not in valid_uids:
                        raise ValueError(
                            f"联盟 {key} 小队 {sq.squad_id} 成员 UID {uid} "
                            f"不在 accounts/enemies 配置中"
                        )
        return self
