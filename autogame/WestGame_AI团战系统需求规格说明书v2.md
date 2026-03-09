---
created: 2026-03-08
type: project
status: active
tags:
  - project
  - westgam
  - ai
  - game-automation
links:
  - "[[wg 团战需求描述prompt]]"
  - "[[cmd_config]]"
---

# WestGame AI 全自动化团战系统 — 需求规格说明书 v2

> [!summary] 摘要
> 本文档是 WestGame AI 全自动化团战系统的**唯一需求来源**。基于实际游戏机制重写，替代 `gemini/` 目录下的早期设计文档。早期文档存在数据模型偏差（HP/energy/buffs/poison_gas 等通用 SLG 概念不适用于本游戏）、关键机制缺失（移城、集结、3 部队系统等）、架构细节不足（未考虑每账号 3 支部队的复杂度）等问题。

---

## 1. 项目概述

### 1.1 项目目标

WestGame 是一款 SLG 手机游戏。本项目是**游戏公司内部探索项目**，目标是让 AI 控制 100 个 NPC 账号，在团战副本中作为真人玩家的陪玩对手，提供有竞争力的游戏体验。

### 1.2 项目范围

- **场景**：全自动化团战副本（2 小时限时，积分制胜负）
- **规模**：AI 管理 100 个游戏内部账号，合计 **300 个行动单元**（每账号 3 支部队）
- **对手**：敌方军团（真人玩家组成），双方总体实力势均力敌

### 1.3 技术前提

- **Server-to-Server**：使用游戏内部 HTTP 接口直接操作账号，无需手机客户端或模拟器
- **无需登录凭证**：从配置文件读取 UID 列表即可操作
- **HTTP 短连接**：Python `requests` 同步调用，服务器同步返回结果
- **无服务器推送**：所有信息需通过命令字主动查询
- **服务器性能充裕**：支持数万 QPS，无频率限制

---

## 2. 游戏机制

> [!info] 重要说明
> 本章节描述的是 WestGame 的**实际游戏机制**，与通用 SLG 概念有显著差异。所有设计决策必须基于此章节，而非通用 SLG 假设。

### 2.1 副本活动规则

- **时限**：2 小时
- **限制**：副本期间**无法补给**（不能采集资源、不能造兵）
- **进入条件**：玩家以**满编兵力**进入副本
- **积分来源**：
  - 据点**首次占领奖励**（一次性积分）
  - 据点**持续占领**产出的时长积分（每分钟累加）
  - **杀敌数量**积分
- **胜负判定**：2 小时结束时，积分高的一方获胜

> [!todo] 待确认
> 积分的具体计算公式（首占奖励值、每分钟积分值、每次击杀积分值）。

### 2.2 地图

- **固定地图**：每次副本使用相同的地图布局
- **坐标系**：1000 × 1000 网格坐标
- **地形**：建筑位置固定，**无地形加成**（不影响战斗结果）
- **无战争迷雾**：可通过接口**实时获取所有敌方信息**（位置、部队状态等）
- **出生位置**：双方各有一个**大本营区域**，进入副本时账号在各自大本营区域内**随机分布**

> [!todo] 待确认
> 地图上建筑的具体布局和数量（大据点 × N 个、小据点 × N 个的分布情况）。双方大本营区域的具体坐标范围。

### 2.3 移城机制

- 玩家可使用**移城指令**将主城瞬间跳转到地图上任意位置
- **无冷却时间、无次数限制**——可以连续移城
- **宝石消耗无限制**：NPC 账号在活动开始前通过 GM 指令大量补充宝石，不会用完
- **移城即全军召回**：移城时所有在外出征的部队**立即收回主城**，全部跟随传送到新坐标
- 这是本游戏的**最强战术操作**——兼具"瞬间传送 + 紧急撤退 + 全军重新部署"三重功能
- 敌方也可以随时移城，因此玩家位置是**实时变化**的
- 对应命令字：`fixed_move_city_new`（需消耗宝石，参数 `tar_pos` 指定目标坐标）

> [!info] 战术意义
> 由于移城无 CD 且秒回部队，AI 可以执行"闪现游击"战术：移城到目标附近 → 出兵攻击 → 战斗结束后移城到下一个目标。这使得距离因素在战略层面被大幅削弱（但行军仍需时间）。

### 2.4 部队系统

> [!info] 关键变更
> 这是与早期设计的**最大差异**。每账号拥有 3 支独立部队，AI 实际管理的是 **300 个行动单元**（100 账号 × 3 部队），而非 100 个。

- 每个账号拥有 **3 支独立部队**，各有独立的英雄和兵种配置
- 3 支部队可以**同时出征**不同目的地
- 典型部署策略：1–2 支用于进攻，1 支留守主城
- **自动防御**：留守主城的部队在敌人攻击主城时自动参与防御战斗
- **伤兵机制**：被击败的部队变为伤兵回城，2 小时内基本无法恢复（等同于永久损失）
- **无体力/行动点限制**：部队可以不间断执行指令

### 2.5 战斗机制

1. 下达进攻指令（`dispatch_troop`）
2. 部队开始**行军**（行军时间随距离**线性增加**）
3. 到达目标后**瞬间结算**战斗
4. 残兵自动回城

**行军速度**：
- 基础速度：**2 秒/格**（即 100 格距离需要 200 秒 ≈ 3.3 分钟）
- 英雄等级可提供行军速度增益（暂不考虑）
- **行军加速道具**：每次使用可减少固定百分比的行军时间，连续使用可大幅缩短实际行军时间（有使用频率上限）

**多路攻击结算方式**：
- 多支部队分别向同一目标发起攻击时，**按到达顺序逐次结算**
- 后到达的部队打到的是前次战斗**剩余的兵力**
- 因此集火攻击的效果优于集结（不用等 5 分钟集结窗口），但无法享受队长的英雄/科技加成

**战斗结果决定因素**：
- 双方兵力数量
- 兵种克制关系：**archer > infantry > cavalry > archer**（三角克制，仅此三种兵种）
- 英雄技能
- 科技等级

**战报查询**：战斗结果可通过接口查询战报获取详细信息。

### 2.6 侦察

- 侦察指令**即时完成**（无行军时间）
- 对应命令字：`dispatch_scout`
- **可获取信息**：
  - 目标的兵力数量
  - 目标的兵种组成
- **无法获取信息**：
  - 英雄等级与技能配置
  - 科技等级
- **注意**：由于**无战争迷雾**，位置信息无需侦察即可获得（通过地图查询接口）

### 2.7 集结机制

集结是本游戏的**核心团战玩法**，允许多个玩家联合攻击同一目标：

1. **队长**发起集结指令 → 开始 **5 分钟窗口期**
2. 窗口期内**队员**派兵加入集结
3. 5 分钟后全部加入的部队**统一开始行军**
4. 到达目标后以集结状态进行战斗

**集结战斗参数**：
- 兵力 = 所有参与者的兵力总和
- 英雄技能 & 科技等级 = **仅取队长的**
- 因此应由**最强账号**担任集结队长

**约束**：
- 每个队长**同时只能发起 1 次集结**
- 每个参与账号（队员）**只能派出 1 支部队**加入集结
- **参与人数上限：15 人**（含队长）
- **总兵力上限**：随队长的科技等级提升而增加（具体数值取决于账号配置）
- **集结可以跨小组**：同一联盟内所有成员都可参与集结，不限于同一 L1 小组
- AI 需根据**距离**判断哪些账号适合参加集结（远距离账号行军时间过长，不宜参与）

> [!info] 架构影响
> 由于集结可跨组，L2 在下达 `RALLY_ATTACK` 指令时需要指定**参与小组列表**，多个 L1 需要协调各自派出哪些账号加入集结。详见 §3.1 L2 指令类型。

> [!todo] 待确认
> - 集结发起/加入的具体命令字。

### 2.8 据点占领

- 派兵**攻击建筑**来占领据点（操作方式类似攻击玩家）
- **中立据点有 NPC 守军**：首次攻占需击败守军，但守军实力较弱，轻易可打掉
- 占领后**需要驻军防守**，否则会被敌方夺回
- 据点分为**大据点**和**小据点**
- **驻军规则**：一个据点只能被一个联盟占有；联盟内每个成员可驻防 **1 支部队**，因此理论上最多可有 100 支部队驻防同一据点

> [!todo] 待确认
> - 大据点 vs 小据点的具体区别（积分差异？防御强度？数量？）
> - 驻防建筑的具体命令字。

**积分产出**：
- 首次占领：一次性奖励积分
- 持续占领：每分钟产出固定积分

### 2.9 账号特征

- 100 个账号的实力呈**金字塔分布**：少数强号 + 多数弱号
- 每个账号有独立的：战力值、英雄配置、兵种配置、科技等级
- **无体力/行动点限制**
- 我方军团与对手军团**总体实力势均力敌**
- **敌方人数不固定**：不超过 100 人，具体数量视对手军团情况而定

---

## 3. 系统架构：递归分层指挥体系

采用分形（Fractal）指挥结构：**上一级的"执行单元"等于下一级的"指挥官"**。将 100 账号（300 部队）的决策空间逐层降维。

```
┌─────────────────────────────────────────────────┐
│         L2 军团指挥官 (Legion Commander)          │
│              1 个 LLM 实例                       │
│         管理 10 个 L1 小队                        │
│         视角：全图战略态势                         │
└────────────────────┬────────────────────────────┘
                     │ 10 条小组级战略指令
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
┌────────┐    ┌────────┐       ┌────────┐
│ L1 队长 │    │ L1 队长 │  ...  │ L1 队长 │  × 10 并行
│ Squad-1 │    │ Squad-2 │       │Squad-10│
│ 10账号  │    │ 10账号  │       │ 10账号  │
│ 30部队  │    │ 30部队  │       │ 30部队  │
└────┬────┘    └────┬────┘       └────┬────┘
     │              │                 │
     ▼              ▼                 ▼
┌─────────────────────────────────────────────────┐
│           L0 执行层 (Executor) — 代码             │
│         指令翻译 + 合法性校验 + HTTP 发送          │
│         管理 300 个行动单元的实际操作              │
└─────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────┐
│           游戏服务器 HTTP 接口                     │
└─────────────────────────────────────────────────┘
```

### 3.0 设计理念：Token 解耦与递归降维

> [!info] 来源：Gemini 对话

采用分层架构的核心动机是**解决 Token 瓶颈**：

- **Token 解耦**：L2 层不需要知道每个兵的兵力，只需要知道"小组"的综合战力；L1 层不需要知道全图所有敌人，只需要知道任务区域的敌人。通过数据抽象，将 100 账号 × 3 部队的海量原始数据，压缩为每层 AI 可消化的精简上下文
- **并行计算**：10 个 L1 小组 AI 可以并行请求 LLM，总耗时 = 最慢的那个 L1 的耗时，而非 10 倍延迟
- **递归可扩展**：如果未来需要管理 1000 个账号，只需增加 L3 层，将"10 个 L2"作为其管理对象，架构代码几乎不变

### 3.1 L2 军团指挥官 (Legion Commander) — 1 个 LLM

**角色定位**：全局战略家。只关心"哪个小组去哪个区域做什么"，不关心具体账号和部队。

| 项目 | 描述 |
|------|------|
| **管理对象** | 10 个 L1 小队 |
| **视场** | 全图战略态势（经聚类抽象后的宏观数据） |
| **输入** | (1) 10 个小队的状态摘要（综合战力、位置重心、交战状态）<br>(2) 全局地图摘要（敌军聚集区热力图、据点归属概览）<br>(3) 活动规则与当前积分<br>(4) 管理员指令（最高优先级）<br>(5) 最近 N 轮的战略决策历史 |
| **输出** | 10 条小组级战略指令 |
| **指令类型** | `ATTACK_BUILDING` / `DEFEND_BUILDING` / `ATTACK_ENEMY_BASE` / `RALLY_ATTACK` / `RETREAT` / `SUPPORT_SQUAD` / `STANDBY` / `JOIN_CROSS_RALLY` |
| **刷新频率** | 每 1–3 分钟（可配置，战况激烈时加快） |
| **关键决策维度** | 积分优劣势分析、时间剩余判断、兵力对比、移城协调、集结时机 |

**L2 战略原则**（来源：Gemini L2 Prompt 设计文档）：
1. **全局观**：决策必须基于整体利益，必要时可以**牺牲局部小组**以换取战略胜利（如让一个小组拖住敌人主力，为其他小组争取占领据点的时间）
2. **协同作战**：主动发动多小组联合进攻（Rally Attack），如让两个小组同时从不同方向夹击同一目标
3. **动态补位**：如果某小组崩溃（战力低于 30%），立刻指派**附近的**健康小组去补位或掩护撤退，而非让远距离小组赶来
4. **避免拥堵**：不要让所有小组都去同一个点，合理分散兵力覆盖多个据点

**L2 数据抽象**（由代码层生成，非原始数据）：
- **友方**：每个小组的综合指标
  - 示例：`"Squad-A: 战力82%, 位置区域北, 状态:交战中"`
- **敌方**：聚类后的威胁区域
  - 示例：`"北区据点附近有约15名敌军集结"`
- **据点**：归属与积分产出概览

### 3.2 L1 小组队长 (Squad Leader) — 10 个 LLM，并行执行

**角色定位**：战术指挥官。将 L2 的战略意图拆解为每个账号、每支部队的具体行动。

| 项目 | 描述 |
|------|------|
| **管理对象** | 10 个账号（每个 3 支部队 = 30 个行动单元） |
| **视场** | 任务区域局部态势（详细坐标级数据） |
| **输入** | (1) L2 下达的战略指令<br>(2) 本组 10 人的详细状态（每人 3 支部队各自的兵力、兵种、英雄、位置、状态）<br>(3) 局部地图详细数据（任务区域内的敌人坐标、建筑状态）<br>(4) 最近 N 轮的战术决策历史与执行结果 |
| **输出** | 每个账号、每支部队的具体行动指令 |
| **指令类型** | `MOVE_CITY` / `ATTACK_TARGET` / `GARRISON_BUILDING` / `JOIN_RALLY` / `INITIATE_RALLY` / `SCOUT` / `RETREAT` / `STANDBY` |
| **刷新频率** | 每 1 分钟 |
| **关键决策维度** | 部队健康度评估、集火目标选择、伤兵/残兵保护、集结人员分配、驻防安排 |

**L1 关键原则**：
1. **生存优先**：重伤部队（兵力 < 30%）不应作为进攻主力
2. **集火攻击**：多支部队集中攻击同一目标
3. **状态一致性**：不对 `MARCHING` / `FIGHTING` 状态的部队下新指令（除非撤退）
4. **守城意识**：确保每个账号至少留 1 支部队守城

### 3.3 L0 执行层 (Executor) — 代码（非 LLM）

**角色定位**：指令翻译器与安全门卫。将 AI 输出的语义指令转为游戏 HTTP 命令字。

| 项目 | 描述 |
|------|------|
| **管理对象** | 实际游戏 HTTP 接口 |
| **输入** | L1 下发的 JSON 格式行动指令 |
| **输出** | HTTP 请求及响应 |
| **校验规则** | 坐标不越界（0–999）、部队状态允许操作、UID 合法、参数格式正确 |
| **异常处理** | 记录错误 → 标记状态 → 下一 loop 反馈给 L1（不重试） |

**L0 指令映射**（AI 语义指令 → 游戏命令字）：

| AI 指令 | 游戏命令字 | 说明 |
|---------|-----------|------|
| `MOVE_CITY` | `fixed_move_city_new` | 移城到指定坐标 |
| `ATTACK_TARGET` | `dispatch_troop` | 派兵攻击目标（玩家或建筑） |
| `SCOUT` | `dispatch_scout` | 侦察目标 |
| `GARRISON_BUILDING` | 待确认 | 派兵驻防建筑 |
| `INITIATE_RALLY` | 待确认 | 发起集结 |
| `JOIN_RALLY` | 待确认 | 加入集结 |

> [!todo] 待确认
> 完整的命令字列表。当前仅有 `cmd_config.yaml` 中的示例命令字，需补充：驻防建筑、集结发起/加入、查询战报、查询积分等。

### 3.4 数据感知层 (Perception Layer)

负责从游戏服务器获取原始数据，并按指挥层级进行**数据抽象**：

```
游戏服务器 HTTP 接口
    ↓ 原始 JSON 数据
数据感知层（Python 代码）
    ├── L0 视图：原始数据直接转发
    ├── L1 视图：本组 10 人详情 + 局部地图（任务区域）
    └── L2 视图：10 组摘要 + 全局热力图（聚类后）
```

**L1 视图构建逻辑**：
- 友方数据：本组 10 人 × 3 部队的完整状态
- 敌方数据：任务区域附近的敌人详细坐标与状态
- 建筑数据：任务区域内的据点归属与驻军情况

**L2 视图构建逻辑**：
- 友方数据：每组聚合为综合指标（战力百分比、位置重心、主要状态）
- 敌方数据：通过聚类算法（如 DBSCAN）将全图敌人归纳为若干威胁区域
- 据点数据：归属状态与积分产出概览

**坐标优化建议**（来源：Gemini 对话）：

> [!info] LLM 空间感知优化
> 直接给 LLM 绝对坐标（如 `[450, 800]`）可能导致其对距离缺乏直觉。建议在数据视图中增加以下辅助信息：
> - **距离标注**：为每个实体附加 `distance_to_target` 字段（如 `"距目标据点: 120格, 预计行军3分钟"`）
> - **相对方位**：可选将坐标转换为相对于小组位置重心的方位描述（如 `"东北方向 80 格"`）
> - **行军时间估算**：将距离转换为预估行军时间，帮助 LLM 判断调度合理性

### 3.5 核心循环（60 秒）

```
Phase 1: Sync (0-5s)
  ├── 并发查询 100 账号状态（含 3 支部队各自状态）
  ├── 获取全图数据（建筑归属、敌方位置）
  ├── 获取积分信息
  └── 读取管理员指令缓冲区

Phase 2: L2 Strategy (5-15s)
  ├── 代码层：将原始数据聚合为 L2 视图
  └── LLM：L2 指挥官生成 10 条小组战略指令

Phase 3: L1 Tactics (15-45s) — 10 个 L1 并行执行
  ├── 代码层：为每个小组构建 L1 视图
  ├── LLM：各 L1 队长生成具体行动指令
  └── 代码层(L0)：校验指令合法性

Phase 4: Action (45-55s) — 流水线模式
  └── 指令生成即发送，不等待所有指令完成

Phase 5: Sleep (55-60s)
  └── 等待下一轮
```

**时间分配说明**：
- Phase 1 使用并发查询，100 个账号同时发起请求
- Phase 2 的 LLM 调用预期 5–10 秒（单次调用）
- Phase 3 的 10 个 L1 **并行执行**，总耗时 = 最慢的那个 L1 的耗时
- Phase 4 采用流水线：L1 每生成一条指令即可发送，无需等待全部完成

### 3.6 通信方式

- HTTP 短连接（Python `requests`）
- 同步返回，无服务器推送，需主动轮询
- 服务器支持数万 QPS，无频率限制

---

## 4. 数据模型

### 4.1 账号状态 (Account)

```yaml
Account:
  uid: string                   # 账号唯一标识
  group_id: string              # 所属小组 ID（如 "squad_1"）
  power: int                    # 综合战力值
  city_pos: [x, y]              # 主城当前坐标
  troops:                       # 3 支独立部队
    - troop_id: int             # 部队编号（1/2/3）
      hero:                     # 英雄信息
        name: string
        level: int
        skills: [string]
      soldiers:                 # 士兵信息
        type: string            # 兵种类型
        count: int              # 当前兵力
        max_count: int          # 满编兵力
      state: enum               # IDLE | MARCHING | FIGHTING | WOUNDED
      position: [x, y]          # 部队当前位置
      target: [x, y] | null    # 目标坐标（行军/战斗时有值）
      arrival_time: timestamp | null  # 预计到达时间
      last_command:              # 上一条执行的指令追踪
        action: string           # 指令类型（如 ATTACK_TARGET）
        target: [x, y] | null   # 指令目标
        status: enum             # EXECUTING | SUCCESS | FAILED
        error_msg: string | null # 失败时的错误信息
```

**部队状态枚举**：

| 状态 | 含义 | 可下达指令 |
|------|------|-----------|
| `IDLE` | 空闲，在主城或驻防点 | 所有指令 |
| `MARCHING` | 行军中 | 仅 `RETREAT`（召回） |
| `FIGHTING` | 战斗中 | 不可操作 |
| `WOUNDED` | 被击败，伤兵回城 | 不可操作（2h 内无法恢复） |

### 4.2 地图实体

#### 建筑 (Building)

```yaml
Building:
  id: string                    # 建筑唯一 ID
  type: enum                    # LARGE | SMALL（大据点/小据点）
  pos: [x, y]                   # 建筑坐标
  owner: enum                   # NEUTRAL | ALLY | ENEMY
  garrison:                     # 驻军列表
    - uid: string               # 驻军玩家 UID
      troop_id: int             # 部队编号
      soldiers:
        type: string
        count: int
  score_per_min: int            # 占领后每分钟产出积分
  first_capture_score: int      # 首次占领奖励积分
```

#### 敌方玩家 (Enemy)

```yaml
Enemy:
  uid: string                   # 敌方 UID
  city_pos: [x, y]              # 主城位置（实时变化，可移城）
  troops:                       # 可见的部队信息
    - soldiers:
        type: string            # 兵种类型
        count: int              # 兵力数量
      state: enum               # IDLE | MARCHING | FIGHTING
      position: [x, y]          # 部队当前位置
      target: [x, y] | null    # 目标坐标
  # 注意：无法获取英雄等级、技能、科技等级
```

### 4.3 积分数据 (Score)

```yaml
Score:
  ally_score: int               # 我方当前总积分
  enemy_score: int              # 敌方当前总积分
  buildings_held:               # 我方占领的建筑列表
    - building_id: string
      since_time: timestamp     # 占领起始时间
  kill_count: int               # 我方击杀总数
  enemy_kill_count: int         # 敌方击杀总数
  time_remaining: int           # 剩余时间（秒）
```

### 4.4 集结数据 (Rally)

```yaml
Rally:
  rally_id: string              # 集结 ID
  leader_uid: string            # 队长 UID
  target: [x, y]                # 攻击目标坐标
  target_type: enum             # BUILDING | PLAYER
  state: enum                   # GATHERING | MARCHING | FIGHTING | COMPLETED
  remaining_time: int           # 集结倒计时（秒，5分钟窗口）
  participants:                 # 参与者列表
    - uid: string
      troop_id: int
      soldiers_count: int
```

---

## 5. AI 决策模块

### 5.1 Prompt 结构（L2 和 L1 共用框架）

每次 LLM 调用的 Prompt 由以下 4 部分组成：

```
┌──────────────────────────────────────────┐
│ Part 1: 静态系统指令                       │
│   角色定义、输出格式约束（JSON）、关键原则    │
├──────────────────────────────────────────┤
│ Part 2: 动态战略输入                       │
│   管理员指令（最高优先级）+ 活动规则 + 积分  │
├──────────────────────────────────────────┤
│ Part 3: 记忆模块                          │
│   最近 N 个 loop 的决策摘要与执行结果       │
├──────────────────────────────────────────┤
│ Part 4: 即时态势                          │
│   按层级抽象的数据视图                      │
└──────────────────────────────────────────┘
```

### 5.2 L2 军团指挥官 Prompt 要点

**思考链 (CoT) 步骤**：
1. **解析管理员意图**：有无新指令？如果有，必须优先执行
2. **评估全局态势**：积分差距、时间剩余、据点分布与归属
3. **分析敌我兵力对比**：哪些小组是生力军？哪些需撤退休整？
4. **制定战术分配**：主力进攻、支援、防守、休整的分配
5. **空间冲突检查**：避免远距离小组执行同一任务（行军时间过长）

**输出要求**：
- 必须为**每个小组**生成一条指令（不可遗漏）
- 只分配区域/任务类型，**不指定具体攻击目标 UID**（那是 L1 的工作）

**输出示例**：
```json
{
  "thinking": "当前积分落后200分，剩余45分钟。北区大据点仍为中立，首占可获大量积分。Squad-1和Squad-3战力充裕且距离较近，命令其跨组集结攻占北区大据点。Squad-7伤亡过半，命令撤退。",
  "orders": {
    "squad_1": {
      "type": "RALLY_ATTACK",
      "target_area": [450, 800],
      "priority": "HIGH",
      "rally_squads": ["squad_1", "squad_3"],
      "rally_leader_squad": "squad_1",
      "description": "发起跨组集结，与 squad_3 联合攻占北区大据点"
    },
    "squad_3": {
      "type": "JOIN_CROSS_RALLY",
      "rally_leader_squad": "squad_1",
      "description": "派兵加入 squad_1 发起的集结"
    },
    "squad_7": {
      "type": "RETREAT",
      "description": "伤亡过半，全组撤退保存实力"
    }
  }
}
```

### 5.3 L1 小队队长 Prompt 要点

**思考链 (CoT) 步骤**：
1. **解析 L2 战略意图**：进攻 / 防守 / 集结 / 撤退？
2. **评估 10 人 × 3 部队的状态**：可用 / 受损 / 忙碌
3. **分析局部威胁**：哪个敌人最危险？最佳攻击点在哪？
4. **分配任务**：
   - 进攻部队（哪些部队去攻击？）
   - 守城部队（每人至少留 1 支）
   - 驻防部队（据点守卫）
   - 集结部队（谁当队长？谁加入？）
5. **坐标校验**：确保目标在地图范围 [0, 999] 内

**输出要求**：
- 每个账号**每支部队**的具体行动指令（JSON 格式）
- 不操作 `MARCHING` / `FIGHTING` 状态的部队（除非撤退）
- 不臆造 UID

**输出示例**：
```json
{
  "thinking": "L2命令集结攻击北区大据点。uid_001战力最高，作为集结队长发起集结。uid_002~005各派1支部队加入集结。所有人各留1支部队守城。uid_008伤兵严重(兵力12%)，不参与进攻。",
  "commands": [
    {
      "uid": "uid_001",
      "troop_id": 1,
      "action": "INITIATE_RALLY",
      "params": { "target_pos": [450, 800], "target_type": "BUILDING" },
      "reason": "作为最强号发起集结"
    },
    {
      "uid": "uid_001",
      "troop_id": 2,
      "action": "STANDBY",
      "reason": "留守主城防御"
    },
    {
      "uid": "uid_002",
      "troop_id": 1,
      "action": "JOIN_RALLY",
      "params": { "rally_id": "uid_001_rally", "troop_id": 1 },
      "reason": "加入集结"
    },
    {
      "uid": "uid_008",
      "troop_id": 1,
      "action": "STANDBY",
      "reason": "兵力仅12%，不适合进攻，留守防御"
    }
  ]
}
```

### 5.4 上下文管理（记忆）

- 保留最近 **5 个 loop** 的历史信息（可通过 `system.yaml` 配置）
- 每个 loop 的记录包括：
  - **态势摘要**：己方兵力变化、积分变化、关键事件（如据点易手、重要部队被歼灭）
  - **下达的指令列表**
  - **执行结果**：成功 / 失败 / 目标消失 / 服务器报错等
- 需要有效的**压缩策略**控制 token 量（每条历史记录不超过 200 tokens）
- **压缩方式**：由 LLM 自行生成历史摘要（而非代码层做硬编码摘要），以保留更灵活的语义信息
- **L2 和 L1 各自维护独立的历史记忆**

### 5.5 LLM 要求

| 项目 | 要求 |
|------|------|
| **响应速度** | 优先（30 秒延迟可接受） |
| **推理能力** | 需要 thinking/reasoning 能力（CoT） |
| **成本** | 暂不限制 |
| **并行** | L1 的 10 个调用必须**并行执行**以控制总延迟 |
| **输出格式** | 必须输出合法 JSON |

---

## 6. 控制模块

### 6.1 配置文件

#### `accounts.yaml` — 账号配置
```yaml
accounts:
  - uid: "uid_001"
    power: 5200000          # 战力值
    tier: S                 # 等级标记（S/A/B/C）
    troops:
      - troop_id: 1
        hero: "hero_name_1"
        soldier_type: "cavalry"
      - troop_id: 2
        hero: "hero_name_2"
        soldier_type: "infantry"
      - troop_id: 3
        hero: "hero_name_3"
        soldier_type: "archer"
  # ... 100 个账号
```

#### `squads.yaml` — 小组分配
```yaml
squads:
  - squad_id: "squad_1"
    members: ["uid_001", "uid_002", ..., "uid_010"]
    rally_leader: "uid_001"    # 集结队长（该组最强号）
  - squad_id: "squad_2"
    members: ["uid_011", "uid_012", ..., "uid_020"]
    rally_leader: "uid_011"
  # ... 10 个小组
```

#### `activity.yaml` — 活动规则
```yaml
activity:
  name: "团战副本"
  duration: 7200              # 2小时 = 7200秒
  map_id: "battle_map_01"
  map_size: [1000, 1000]
  scoring:
    first_capture_large: 500  # 大据点首占积分（待确认）
    first_capture_small: 200  # 小据点首占积分（待确认）
    hold_per_min_large: 10    # 大据点每分钟积分（待确认）
    hold_per_min_small: 5     # 小据点每分钟积分（待确认）
    kill_score: 1             # 每次击杀积分（待确认）
  buildings:                  # 建筑列表
    - id: "building_01"
      type: LARGE
      pos: [500, 500]
    # ... 所有建筑的坐标和类型
```

#### `system.yaml` — 系统配置
```yaml
system:
  loop_interval: 60           # 主循环间隔（秒）
  l2_interval: 120            # L2 决策间隔（秒），可动态调整
  history_limit: 5            # 保留历史 loop 数量
  llm:
    provider: "tbd"           # LLM 服务商（待定）
    model: "tbd"              # 模型名称
    timeout: 30               # 单次调用超时（秒）
    temperature: 0.3          # 低温度以获得稳定输出
  game_server:
    base_url: "http://internal-game-server"
    timeout: 5                # HTTP 超时（秒）
```

### 6.2 命令字接口

基于 `cmd_config.yaml` 中已有的命令字，扩展完整列表：

**已确认的命令字**：

| 操作 | 命令字 | 关键参数 |
|------|--------|---------|
| 移城 | `fixed_move_city_new` | `tar_pos`, `use_gem`, `item_id` |
| 攻击玩家 | `dispatch_troop` | `target_type: 2`, `march_type: 2` |
| 侦察 | `dispatch_scout` | `tar_type: 5`, `scout_queue_id: 8001` |
| 获取玩家坐标 | `login_get` | `list: ["svr_lord_info_new"]` |
| 添加宝石 | `op_self_set_gem` | `gem_num` |
| 添加士兵 | `op_add_soldiers` | `soldier_id`, `soldier_num` |
| 添加资源 | `op_self_add_clear_resource` | `op_type: 0` |

> [!todo] 待确认
> 需补充以下命令字：
> - [ ] 攻击建筑（占领据点）
> - [ ] 驻防建筑
> - [ ] 发起集结
> - [ ] 加入集结
> - [ ] 查询战报
> - [ ] 查询积分
> - [ ] 查询地图建筑状态
> - [ ] 查询全图玩家位置
> - [ ] 召回行军中的部队

### 6.3 管理员 CLI

- **交互方式**：命令行交互式界面
- **输入方式**：自然语言（如："优先进攻1号建筑"、"防守为主"、"全军撤退"）
- **优先级**：最高，下一 loop 生效
- **限制**：不能接管具体账号的操作（只能下达战略级指令）
- **注入机制**：管理员输入写入指令缓冲区，L2 在下一个 loop 的 Phase 2 读取并执行

---

## 7. 异常处理

| 异常类型 | 处理策略 |
|---------|---------|
| **命令执行失败**（服务器返回错误） | 不实时处理。记录错误日志，标记状态，下一 loop L1 重新决策 |
| **LLM 输出格式错误**（JSON 解析失败） | L0 拒绝发送。错误信息反馈给下一 loop 的 Prompt |
| **LLM 语义错误**（指令参数非法） | L0 校验拒绝。服务端返回无效，反馈给下一 loop |
| **LLM 服务不可用**（超时/宕机） | 暂停所有操作，全军原地待命，持续重试连接 |
| **LLM 连续多轮输出失败** | 暂停所有操作，等待人工介入 |
| **LLM 调用超时**（单个 L1 超时） | 跳过该小组本轮操作，其他 9 组正常执行 |
| **单个账号异常**（掉线/封禁） | 跳过该账号，不中断 loop，从小组名单中临时剔除 |
| **目标消失**（敌人已移城/部队已撤退） | 服务端返回目标不存在，下一 loop 重新决策 |

**核心原则**：所有异常都不做实时重试，统一延迟到下一 loop 处理。保证系统健壮性和决策一致性。

---

## 8. 日志系统

### 8.1 日志内容

每个 loop 记录以下信息：

- **Loop 元信息**：loop 编号、开始/结束时间、各 phase 耗时
- **LLM 调用日志**：
  - L2 完整 Prompt（输入）
  - L2 完整响应（输出）
  - 每个 L1 的完整 Prompt（输入）
  - 每个 L1 的完整响应（输出）
- **指令执行日志**：所有发送到游戏服务器的命令及其响应
- **状态快照**：每 loop 开始时的全量状态数据

### 8.2 存储方式

- **持久化到文件系统**（按日期/loop 编号组织）
- **目录结构示例**：
  ```
  logs/
    2026-03-08/
      loop_001/
        l2_prompt.json
        l2_response.json
        l1_squad_1_prompt.json
        l1_squad_1_response.json
        ...
        commands_sent.json
        state_snapshot.json
      loop_002/
        ...
  ```
- 暂不需要可视化（未来可扩展为 Web Dashboard）

---

## 9. 技术选型

| 项目 | 选择 | 说明 |
|------|------|------|
| **语言** | Python | 生态成熟，LLM SDK 支持好 |
| **HTTP 库** | `requests`（同步）或 `aiohttp`（异步） | 如需并发查询性能优化可选 `aiohttp` |
| **并发框架** | `asyncio` | L1 并行调用、并发查询状态 |
| **状态管理** | 内存 | 无需数据库，所有状态在进程内维护 |
| **日志** | 文件系统 | JSON 格式，按 loop 组织 |
| **LLM** | 待定 | 要求：thinking 能力、JSON 输出、响应速度优先 |
| **配置格式** | YAML | 人类可读，易于编辑 |

---

## 10. 开发路线图

> [!info] 来源：Gemini 对话综合设计文档

建议按以下阶段推进开发，每阶段约 1 周：

### Phase 1: 基础设施建设

- [ ] **Mock 服务器**：按附录 A 的设计搭建模拟游戏服务器（FastAPI），实现命令字路由、内存世界状态、模拟引擎
- [ ] **Data Schema**：使用 Python Pydantic 定义数据模型（Account、Building、Enemy、Rally、Score），确保 JSON 序列化/反序列化正确
- [ ] **Loop Framework**：实现 AsyncIO 主循环骨架，打通并发请求链路（空转循环，不接 LLM）
- [ ] **配置加载**：实现 `accounts.yaml`、`squads.yaml`、`activity.yaml`、`system.yaml` 的读取与校验

### Phase 2: 单小组智能验证

- [ ] **Prompt 调试**：使用 1 个小组（10 账号，30 部队）进行测试，调整 L1 Prompt 使 AI 能稳定理解"集火"、"守城"、"集结"等战术逻辑
- [ ] **Guardrails 开发**：编写 L0 执行层的规则校验器（坐标越界检查、部队状态冲突检查、UID 合法性）
- [ ] **状态机联动**：确保 `MARCHING` / `FIGHTING` 状态的部队不会被 AI 重复下达指令
- [ ] **JSON 输出稳定性**：测试 LLM 输出的 JSON 格式合法率，必要时添加重试或格式修复逻辑

### Phase 3: 多小组并发与 L2 接入

- [ ] **扩容测试**：开启 10 个小组并行，监控 LLM Token 消耗速率与响应延迟
- [ ] **L2 开发**：实现军团指挥官 AI，测试其能否根据全图态势生成合理的小组级战略指令
- [ ] **记忆模块**：实现 loop 历史记录的存储与压缩（控制每条不超过 200 tokens）
- [ ] **管理员 CLI**：实现命令行交互界面，支持自然语言指令注入

### Phase 4: 实战演练与调优

- [ ] **对抗测试**：在真实/模拟环境中投放 100 个 AI 账号，观察与脚本敌人的对抗效果
- [ ] **参数调优**：调整 Loop 间隔、LLM Temperature、L2 决策频率、历史保留数量等
- [ ] **日志分析**：通过回放日志分析 AI 的决策质量，识别常见错误模式
- [ ] **移城策略**：重点调优移城时机与坐标选择，这是影响胜负的关键战术

---

## 11. 待确认项汇总

以下事项需要在开发前与游戏策划/服务端团队确认：

- [ ] **积分计算公式**：首占奖励值、每分钟持续积分值、击杀积分值的具体数值
- [ ] **大据点 vs 小据点**的具体区别（积分差异、防御强度、地图上的数量与分布）
- [ ] **完整的命令字列表**（当前仅有 `cmd_config.yaml` 中的 7 个示例）
- [ ] **地图建筑的具体布局**和数量
- [ ] **双方大本营区域的具体坐标范围**
- [ ] **集结相关命令字**（发起集结、加入集结）
- [ ] **驻防建筑命令字**
- [ ] **查询战报命令字**
- [ ] **查询积分命令字**
- [ ] **召回行军中部队的命令字**
- [ ] **行军加速道具的命令字**及使用频率上限
- [ ] **真实游戏服务器的 HTTP 请求格式**（URL 结构、认证方式、完整请求/响应示例）——开发时提供
- [ ] **中立据点 NPC 守军的具体强度**（兵力数值）

---

## 12. Q&A：已确认的游戏机制

以下问题已与需求方确认，作为设计依据。

### 移城机制

**Q1: 移城是否有冷却时间？**
A: 完全没有冷却时间及次数的限制。

**Q2: 移城消耗的宝石是否无限？**
A: 宝石无限制。在活动开始前会用 GM 指令大量补充，绝对不会用完。

**Q8: 移城后，已出征的部队怎么办？**
A: 在外的军队会秒收回主城，全部移到新坐标。

> [!info] 战术影响
> 移城 = 瞬间传送 + 全军召回 + 重新部署。这使其成为游戏中最强的战术操作，AI 需要充分利用。

### 行军与战斗

**Q3: 行军速度的具体数值？不同兵种速度是否不同？**
A: 行军速度是 2 秒一格。英雄等级升高后有增益，在此暂不考虑。更重要的是有行军加速道具，每次使用可以减少固定百分比的行军时间。连续使用后可以大幅缩短实际行军时间（为公平起见，有使用频率的上限）。

**Q4: 兵种有哪几种？**
A: 仅有三种：cavalry / infantry / archer。

**Q5: 兵种克制关系的具体数值？**
A: archer > infantry > cavalry > archer。无具体克制数值。

**Q13: 战斗是否支持多路同时攻击同一目标？**
A: 分 3 次先后结算。后结算者会打到对方上一次剩余下来的兵力。

### 集结机制

**Q11: 集结是否可以跨小组？**
A: 同一个联盟内的成员都可以参与集结。由于集结需要行军时间，AI 要决定仅让距离较近的玩家参加。

**Q12: 一个账号能否派多支部队加入同一个集结？**
A: 一个账号只能发起一次集结（队长）。参与账号（队员）也只能派出一支部队。集结总人数上限为 15 人（含队长），且有总兵力上限（随队长科技等级提升增加）。

### 据点与地图

**Q7: 双方出生位置在哪？**
A: 在我方大本营指定区域内随机分布。

**Q9: 据点驻军上限？**
A: 一个据点只能被一个联盟占有。每个联盟成员可以驻防一支军队。也就是说最多有与联盟成员数量相等的军队驻防。

**Q10: 中立据点是否有初始防御力？**
A: 中立据点有初始防御力。第一次攻占时需要打败 NPC 守军，但这个守军实力较弱，轻易就可以打掉。

### 对手信息

**Q14: 敌方账号数量？**
A: 不确定。不超过 100 人。

### 系统设计

**Q6: 真实游戏服务器的 HTTP 请求格式？**
A: 开发时提供。

**Q15: L2 和 L1 的 Token 预算？**
A: 无预算上限。

**Q16: LLM JSON 输出连续多轮失败时的策略？**
A: 多轮失败情况下暂停所有动作。

**Q17: 记忆压缩的具体策略？**
A: 让 LLM 自己做总结。

**Q18: 活动开始前是否有准备阶段？**
A: 有准备阶段。仅对人类玩家有用。AI 军团可以直接从配置中了解地图和战略。

---

## 关联

- [[wg 团战需求描述prompt]] — 早期需求讨论记录
- [[cmd_config]] — 已知命令字配置
- `gemini/` 目录 — 早期设计文档（已被本文档替代，仅作参考）

---

## 附录 A: Mock 游戏服务器设计

### A.1 设计目标

Mock 服务器用于在**无真实游戏环境**下进行端到端测试，验证 AI 系统从 L2 战略决策到 L0 指令执行的完整链路。

**核心要求**：
- 接受与真实游戏服务器相同格式的 HTTP 命令字请求
- 维护**有状态的内存世界**：部队位置、兵力、据点归属等随指令执行而变化
- 模拟行军时间、战斗结算等关键游戏行为，使 AI 能产生有意义的多轮决策
- 同时模拟敌方行为（简单脚本 AI），让战场具备对抗性

### A.2 架构概览

```
┌─────────────────────────────────────────────────┐
│              AI Controller (被测系统)              │
│         发送命令字 / 查询状态                       │
└────────────────────┬────────────────────────────┘
                     │ HTTP (同 真实服务器接口)
                     ▼
┌─────────────────────────────────────────────────┐
│              Mock Game Server                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ HTTP API │  │ 世界状态  │  │ 模拟引擎     │  │
│  │ 路由层   │→│ (内存)    │←│ (Tick 驱动)  │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│                      ↑                           │
│               ┌──────┴──────┐                    │
│               │ 预置场景    │                    │
│               │ (Fixtures)  │                    │
│               └─────────────┘                    │
└─────────────────────────────────────────────────┘
```

### A.3 HTTP API 设计

Mock 服务器暴露**单一入口**，与真实游戏服务器保持一致：

**请求格式**：
```
POST /api/game
Content-Type: application/json

{
  "uid": "uid_001",           // 操作账号
  "cmd": "dispatch_troop",    // 命令字
  "params": {                 // 命令参数
    "target_type": 2,
    "march_type": 2,
    "tar_pos": [450, 800],
    "troop_id": 1
  }
}
```

**响应格式**：
```json
{
  "code": 0,                  // 0=成功, 非0=失败
  "msg": "ok",
  "data": { ... }             // 命令特定的返回数据
}
```

### A.4 支持的命令字与 Mock 行为

| 命令字 | Mock 行为 | 返回数据 |
|--------|----------|---------|
| **`login_get`** | 返回指定 UID 的当前状态（坐标、部队、战力等） | 账号完整状态 JSON |
| **`fixed_move_city_new`** | 立即更新内存中该账号的 `city_pos` 为 `tar_pos` | `{ "new_pos": [x, y] }` |
| **`dispatch_troop`** | 将指定部队状态设为 `MARCHING`，计算 `arrival_time`（基于距离） | `{ "march_id": "xxx", "arrival_time": timestamp }` |
| **`dispatch_scout`** | 即时返回目标的兵力和兵种信息（从内存世界读取） | `{ "troops": [...] }` |
| **`query_map`** | 返回全图建筑归属、所有可见玩家位置 | 全图快照 JSON |
| **`query_battle_report`** | 返回最近的战报列表 | `{ "reports": [...] }` |
| **`query_score`** | 返回双方当前积分、剩余时间 | Score 数据结构 |
| **`garrison_building`** | 将部队状态设为驻防，更新建筑驻军列表 | `{ "garrison_id": "xxx" }` |
| **`initiate_rally`** | 创建集结实例，开始 5 分钟倒计时 | `{ "rally_id": "xxx" }` |
| **`join_rally`** | 将部队加入指定集结 | `{ "joined": true }` |
| **`recall_troop`** | 将行军中的部队状态改为返程 | `{ "recalled": true }` |

> [!info] 对于尚未确认命令字的操作（如 `garrison_building`），Mock 可以先使用占位命令字名称，待真实接口确认后再更新。

### A.5 内存世界状态

Mock 服务器启动时从 **Fixture 文件** 加载初始世界状态：

#### `mock_world.yaml` — 初始世界配置

```yaml
world:
  time_remaining: 7200        # 副本剩余时间（秒）
  tick_interval: 1             # 模拟引擎 tick 间隔（秒）

  ally_accounts:               # 我方 100 个账号（从 accounts.yaml 加载）
    # 自动加载，初始状态：满编兵力，随机分布在我方出生区域

  enemy_accounts:              # 敌方模拟账号
    count: 80                  # 敌方账号数量
    spawn_zone: [600, 600, 999, 999]  # 出生区域 [x_min, y_min, x_max, y_max]
    power_distribution: "pyramid"      # 金字塔分布，与我方对称
    ai_mode: "simple_script"           # 敌方 AI 模式（见 A.7）

  buildings:                   # 据点列表
    - id: "bld_large_01"
      type: LARGE
      pos: [500, 500]
      owner: NEUTRAL
      garrison: []
      first_capture_score: 500
      score_per_min: 10
    - id: "bld_small_01"
      type: SMALL
      pos: [300, 700]
      owner: NEUTRAL
      garrison: []
      first_capture_score: 200
      score_per_min: 5
    # ... 更多据点

  score:
    ally: 0
    enemy: 0
```

### A.6 模拟引擎 (Simulation Engine)

Mock 服务器内部运行一个 **Tick 驱动的模拟引擎**，每秒更新世界状态：

#### 行军模拟
```python
# 每 tick 检查所有 MARCHING 状态的部队
for troop in all_marching_troops:
    if current_time >= troop.arrival_time:
        # 到达目标
        if troop.target_type == "PLAYER":
            resolve_battle(troop, target_player)
        elif troop.target_type == "BUILDING":
            resolve_capture(troop, target_building)
        troop.state = "IDLE"
```

#### 战斗结算（简化模型）
```python
def resolve_battle(attacker_troops, defender_troops):
    """简化战斗：按兵力比例计算损失"""
    atk_power = sum(t.count * get_type_modifier(t.type) for t in attacker_troops)
    def_power = sum(t.count * get_type_modifier(t.type) for t in defender_troops)

    ratio = atk_power / (atk_power + def_power)

    if ratio > 0.5:  # 进攻方胜
        atk_loss_rate = 0.3 * (1 - ratio)   # 优势越大损失越小
        def_loss_rate = 0.7 + 0.3 * ratio    # 劣势方损失更大
        winner = "attacker"
    else:             # 防守方胜
        atk_loss_rate = 0.7 + 0.3 * (1 - ratio)
        def_loss_rate = 0.3 * ratio
        winner = "defender"

    # 扣除兵力
    for t in attacker_troops:
        t.count = int(t.count * (1 - atk_loss_rate))
    for t in defender_troops:
        t.count = int(t.count * (1 - def_loss_rate))

    # 兵力归零的部队 → WOUNDED 状态
    # 生成战报记录

    return BattleReport(winner, atk_loss_rate, def_loss_rate)
```

#### 兵种克制系数

```python
# 简化的兵种克制表：骑兵 > 弓兵 > 步兵 > 骑兵
TYPE_MODIFIERS = {
    ("cavalry", "archer"):   1.3,   # 骑兵打弓兵加成
    ("archer", "infantry"):  1.3,   # 弓兵打步兵加成
    ("infantry", "cavalry"): 1.3,   # 步兵打骑兵加成
    # 反向被克制
    ("archer", "cavalry"):   0.7,
    ("infantry", "archer"):  0.7,
    ("cavalry", "infantry"): 0.7,
}
```

#### 行军时间计算
```python
def calc_march_time(from_pos, to_pos, speed=1.0):
    """距离线性映射到行军时间"""
    distance = math.sqrt((from_pos[0]-to_pos[0])**2 + (from_pos[1]-to_pos[1])**2)
    # 每 100 格约 60 秒（可配置）
    return distance / 100 * 60 / speed
```

#### 积分更新
```python
# 每分钟 tick
for building in buildings:
    if building.owner == "ALLY":
        score["ally"] += building.score_per_min
    elif building.owner == "ENEMY":
        score["enemy"] += building.score_per_min
```

#### 集结模拟
```python
# 集结状态机
for rally in active_rallies:
    if rally.state == "GATHERING":
        if current_time >= rally.created_time + 300:  # 5分钟窗口
            rally.state = "MARCHING"
            rally.arrival_time = current_time + calc_march_time(
                rally.leader_pos, rally.target_pos
            )
    elif rally.state == "MARCHING":
        if current_time >= rally.arrival_time:
            resolve_battle(rally.all_troops, target_troops)
            rally.state = "COMPLETED"
```

### A.7 敌方模拟 AI

为了让战场具备对抗性，Mock 服务器内置简单的敌方脚本 AI：

| 模式 | 行为 | 适用场景 |
|------|------|---------|
| **`passive`** | 敌方完全不动，仅驻防据点 | 基础功能测试，验证我方 AI 能正常攻占 |
| **`simple_script`** | 每 2 分钟随机占领 1 个中立据点；被攻击时 50% 概率移城逃跑 | 常规测试，验证 AI 的进攻/防守切换 |
| **`aggressive`** | 主动集结进攻我方据点；优先攻击兵力最少的我方账号 | 压力测试，验证 AI 的防御和补位能力 |
| **`mirror`** | 镜像复制我方 AI 的行为模式（延迟 1 轮） | 对称对抗测试 |

```yaml
# mock_config.yaml 中配置
enemy_ai:
  mode: "simple_script"        # passive | simple_script | aggressive | mirror
  decision_interval: 120       # 决策间隔（秒）
  aggression: 0.5              # 攻击倾向 0.0~1.0
```

### A.8 测试场景预设 (Fixtures)

提供多个预置场景，覆盖不同测试需求：

| 场景 | 文件名 | 描述 |
|------|--------|------|
| **冷启动** | `fixture_cold_start.yaml` | 双方满编、所有据点中立、从两端出发。测试 AI 的初始部署策略 |
| **中期拉锯** | `fixture_mid_game.yaml` | 活动已进行 60 分钟、双方各占 3 个据点、部分部队受损。测试 AI 的中期决策 |
| **劣势翻盘** | `fixture_losing.yaml` | 我方积分落后 30%、2 个小组重伤、敌方控制大据点。测试 AI 的逆境决策 |
| **集结攻坚** | `fixture_rally_test.yaml` | 敌方重兵驻守大据点、我方需集结攻坚。专项测试集结机制 |
| **多线作战** | `fixture_multi_front.yaml` | 敌方从 3 个方向同时进攻。测试 AI 的兵力分配与补位 |

### A.9 日志与调试

Mock 服务器记录所有交互，便于调试 AI 行为：

```
mock_logs/
  session_2026-03-09/
    requests.jsonl          # 所有收到的 HTTP 请求（时间戳 + uid + cmd + params）
    world_snapshots/        # 每 60 秒一次的世界状态快照
      tick_0000.json
      tick_0060.json
      ...
    battle_reports.jsonl    # 所有战斗结算记录
    score_timeline.csv      # 积分变化时间线（可直接绘图）
```

**调试工具**：
- **快进模式**：`--speed 10x` 将模拟时间加速 10 倍，2 小时副本在 12 分钟内跑完
- **暂停/步进**：`--pause` 暂停模拟引擎，手动触发单次 tick，逐步观察 AI 决策
- **状态注入**：`POST /debug/set_state` 接口，运行时手动修改世界状态（如强制设置某账号兵力为 0）
- **回放模式**：加载历史 `world_snapshots` 重新播放，支持从任意时间点重启测试

### A.10 技术选型

| 项目 | 选择 | 说明 |
|------|------|------|
| **框架** | FastAPI | 轻量、异步、自动生成 API 文档 |
| **状态存储** | 内存字典 | 无需持久化，进程重启即重置 |
| **模拟引擎** | `asyncio` 后台任务 | 与 HTTP 服务共享事件循环 |
| **Fixture 格式** | YAML | 与主系统配置格式一致 |
| **日志** | JSONL（逐行 JSON） | 便于程序解析和 `jq` 查询 |

---

## 附录 B: Python AsyncIO 核心控制循环伪代码（原附录 A）

> [!info] 来源：Gemini 对话中的工程实现逻辑
> 以下伪代码展示了主循环的并发架构，可作为实际开发的起点。

```python
import asyncio
import time
from typing import List, Dict

LOOP_INTERVAL = 60   # 秒
LLM_TIMEOUT = 30     # 秒

class AIController:
    def __init__(self):
        self.game_api = GameAPI()
        self.llm = LLMService()
        self.squads = load_squads_from_config()  # 10 个小组
        self.admin_orders = []  # 管理员指令缓冲区

    async def run_loop(self):
        while True:
            start = time.time()

            # Phase 1: Sync — 并发查询所有状态
            map_task = self.game_api.get_map_data()
            status_tasks = [self.game_api.get_squad_status(s) for s in self.squads]
            results = await asyncio.gather(map_task, *status_tasks, return_exceptions=True)
            global_map, squad_statuses = results[0], results[1:]

            # Phase 2: L2 Strategy — 生成 10 条小组级指令
            squad_summaries = [summarize(s, st) for s, st in zip(self.squads, squad_statuses)]
            l2_orders = await self.llm.think_l2(global_map, squad_summaries, self.admin_orders)

            # Phase 3: L1 Tactics — 10 个小组并行思考
            l1_tasks = []
            for squad, status in zip(self.squads, squad_statuses):
                context = build_l1_context(squad, status, l2_orders, global_map)
                l1_tasks.append(self.process_squad(squad, context))
            await asyncio.gather(*l1_tasks)

            # Phase 4: Sleep
            self.admin_orders.clear()
            elapsed = time.time() - start
            await asyncio.sleep(max(0, LOOP_INTERVAL - elapsed))

    async def process_squad(self, squad, context):
        """单个小组的完整处理：LLM 思考 → 校验 → 执行"""
        try:
            response = await asyncio.wait_for(
                self.llm.think_l1(context), timeout=LLM_TIMEOUT
            )
            valid_cmds = [c for c in response.get("commands", [])
                          if validate_command(c, squad)]
            # 流水线发送：生成即发送，不等待全部完成
            send_tasks = [self.game_api.send_command(c["uid"], c) for c in valid_cmds]
            await asyncio.gather(*send_tasks, return_exceptions=True)
            squad.history.append(summarize_loop_result(response, valid_cmds))
        except asyncio.TimeoutError:
            pass  # 跳过本轮，不阻塞其他小组
        except Exception as e:
            log_error(squad.id, e)  # 记录错误，下一 loop 处理
```

**关键实现要点**：
1. **`asyncio.gather(*tasks, return_exceptions=True)`**：确保单个任务失败不会导致整体崩溃
2. **`asyncio.wait_for(timeout=30)`**：LLM 超时控制，保证系统不因单个 L1 卡住而停滞
3. **流水线发送**：L1 每产生一条有效指令即可发送，无需等待所有小组思考完毕
4. **`_filter_map_for_squad()`**（未展示）：根据小组位置裁剪地图数据，只保留任务区域附近的敌人信息，显著减少 Token 消耗
