# Prompt Record

- Date: 2026-03-10 23:30
- Branch: master
- Commit: implement P0 config system: schemas, loader, and 4 YAML files

---

### 1

Implement the following plan:

# P0 配置系统实现计划

## Context

Phase 1 基础设施已完成 ~60%（Game API、CLI、Mock Server、Pydantic 数据模型）。下一步是 P0 配置系统，它是主循环、数据同步、L0 执行器的前置依赖。用户要求先做 20 个账号（4 小队×5人 + 2 备用），而非完整 100 个。

## 要创建/修改的文件（6个）

### 1. `config/accounts.yaml` — 账号配置
- 20 个账号，UID 由用户指定
- 每个账号字段：`uid`, `name`（可选标签，方便日志辨识）
- 保持最小化，运行时详细信息（战力、兵种等）从服务器同步获取

### 2. `config/squads.yaml` — 小队分配
- 4 个小队，每队 5 人
- 按 UID 列表顺序分配：413-417 → squad_1, 418-422 → squad_2, 423-427 → squad_3, 428-432 → squad_4

### 3. `config/activity.yaml` — 活动规则
- 副本时长、地图尺寸、积分规则等（基于需求文档）
- 用合理默认值，待实战调整

### 4. `config/system.yaml` — 系统参数
- 主循环间隔（60s）、LLM 超时（30s）、并发限制、日志级别等

### 5. `src/config/schemas.py` — Pydantic v2 配置 Schema
- 类：`AccountEntry`, `ReserveEntry`, `AccountsConfig`, `SquadEntry`, `SquadsConfig`, `ActivityConfig`, `SystemConfig`, `AppConfig`（顶层聚合）

### 6. `src/config/loader.py` — 配置加载器
- `load_yaml`, `load_accounts`, `load_squads`, `load_activity`, `load_system`, `load_all`
- 校验：小队成员 UID 必须存在于 accounts 列表中

## 设计决策

1. 账号配置最小化：只存 uid + name，运行时信息从服务器拉取
2. AppConfig 聚合：一个顶层对象持有所有配置
3. reserves 独立字段：备用账号不属于任何小队

> **Insight**
> 1. 已有模型风格：Pydantic v2 BaseModel, `Field(default_factory=...)`, snake_case, IntEnum, tuple coords
> 2. 配置系统采用**两层分离**：YAML 文件存静态配置 → Pydantic schema 做加载时校验 → loader 做跨文件交叉校验（如小队 UID ∈ 账号列表）
> 3. `AppConfig` 聚合模式让主循环只需接收一个对象，避免到处传递零散配置

> **Insight (post-implementation)**
> 1. **多层校验策略**：每层 schema 各守一关 — `AccountsConfig` 查 UID 唯一性，`SquadEntry` 查队长∈成员，`SquadsConfig` 查跨队不重复，`AppConfig` 做终极交叉校验（小队 UID ∈ 账号列表）
> 2. **配置最小化原则**：accounts.yaml 只存 `uid + name`，所有运行时数据由 `data_sync` 从服务器拉取 → 消除配置与服务器状态不一致的风险
> 3. **AppConfig 单入口**：主循环只需 `cfg = load_all("config")` 一行

**Files:** `config/accounts.yaml`, `config/squads.yaml`, `config/activity.yaml`, `config/system.yaml`, `src/config/schemas.py`, `src/config/loader.py`

### 2

更新一下progress.md

**Files:** `docs/progress.md`
