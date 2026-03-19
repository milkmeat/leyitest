# WestGame AI 团战系统 — 开发进度

> 最后更新: 2026-03-19 (Phase 3 推进 — L2+L1 联合测试脚本完成 ✅)

---

## Phase 1: 基础设施

> Mock Server + Pydantic 数据模型 + 主循环骨架 + 配置加载

### 已完成

| 组件 | 文件 | 提交 | 说明 |
|------|------|------|------|
| 命令字配置 | `src/config/cmd_config.yaml` | `0a4ae11` | 18个命令字完整定义（行动9+查询5+GM3+集结1） |
| 环境配置 | `config/env_config.yaml` | `7eb2d17` | test/mock 双环境，请求头默认值 |
| 坐标工具 | `src/utils/coords.py` | `2e091fb` | `encode_pos`/`decode_pos`，坐标 ↔ 整数编码 |
| Game API 客户端 | `src/executor/game_api.py` | `08c9b58` | 异步HTTP客户端，18个便捷方法，队列批量发送 |
| CLI 入口 | `src/main.py` | `17f27a6` | 完整命令行工具，18个命令，支持 `--mock` 切换 |
| Mock Server 路由 | `mock_server/app.py` | `17f27a6` | FastAPI，15个命令处理器，GET协议 |
| Mock 测试数据 | `mock_server/mock_data.yaml` | `c803dfa` | 2个测试玩家 + 2个建筑（最小可用） |
| LLM Prompt 模板 | `src/ai/prompts/*.txt` | `7eb2d17` | L2/L1 系统提示词 |
| 依赖声明 | `requirements.txt` | `7eb2d17` | pydantic/aiohttp/fastapi/numpy/sklearn |
| **Pydantic 数据模型** | `src/models/*.py` | `f2a4aa5` | 5个模型文件，基于 test server 真实返回构建 |
| 数据采集脚本 | `scripts/collect_samples.py` | `f2a4aa5` | 批量采集 test server 响应到 `docs/samples/` |
| 服务端响应样本 | `docs/samples/*.json` | `f2a4aa5` | 14个 JSON 样本，覆盖主要查询命令 |
| **配置 Schema** | `src/config/schemas.py` | `218e752` | 8个 Pydantic v2 模型 + 4层校验（UID唯一/队长∈成员/跨队不重复/交叉引用） |
| **配置加载器** | `src/config/loader.py` | `218e752` | YAML 加载 + `load_all()` 一站式聚合 |
| **账号配置** | `config/accounts.yaml` | `218e752` | 20账号 (UID 20010413-432) + 2备用 |
| **小队配置** | `config/squads.yaml` | `218e752` | 4小队×5人 (Alpha/Bravo/Charlie/Delta) |
| **活动规则** | `config/activity.yaml` | `218e752` | 2h副本、1000×1000地图、克制系数、积分规则 |
| **系统参数** | `config/system.yaml` | `218e752` | 主循环60s、LLM超时30s、并发限制 |
| **L0 执行器** | `src/executor/l0_executor.py` | `0947ad7` | 264行，7种AI指令→游戏命令翻译 + UID/坐标/部队状态校验 |
| **L0 集成测试** | `test_l0.sh` | `20385b5` | CLI文本命令集成测试，覆盖所有L0指令类型 |
| **单兵攻击测试** | `test_solo.sh` | `4d4d2ae` | 端到端: 账号A攻击账号B，验证 march_info 流程 |
| **数据同步** | `src/perception/data_sync.py` | `e8a193d` | 246行，并发账号同步+地图解析，CLI `sync` 命令 |
| **同步集成测试** | `test_sync.sh` | `e8a193d` | 10项测试: 全量/单账号同步 + JSON输出 |
| **主循环** | `src/controller/loop.py` | `848cbb3` | AIController 5阶段编排(Sync→L2 stub→L1 stub→Action→Sleep) + LoopStats + JSON日志 |
| **run CLI 命令** | `src/main.py` | `848cbb3` | `run --rounds/--once/--loop.interval_seconds` 参数支持 |
| **主循环测试** | `test_loop.sh` | `848cbb3` | 12项测试: 单轮/多轮/阶段标记/stub/日志文件 |
| **Phase 1 验收** | `test_phase1.sh` | `848cbb3` | 4个测试套件串联验收: sync+l0+solo+loop 全部通过 |

### 待完成（Phase 1 后续可选）

| 优先级 | 组件 | 文件 | 说明 |
|--------|------|------|------|
| P2 | Mock 世界状态 | `mock_server/world_state.py` | 内存世界状态管理 |
| P2 | Mock 模拟引擎 | `mock_server/simulation.py` | Tick驱动行军/积分模拟 |
| P2 | Mock 战斗结算 | `mock_server/battle.py` | 兵种克制战斗计算 |
| P2 | Mock 敌方AI | `mock_server/enemy_ai.py` | 4种敌方脚本模式 |

### 备注

- Pydantic 模型中 `Troop`（在外部队）字段基于 `marchBasic` 结构推断，待实际派兵后用真实数据校验
- `Rally` 和 `Score` 模型基于需求文档设计，测试环境暂无活跃样本
- `get_map_overview` 需要 `sid=1`（不是默认的 0），已在采集脚本中修正
- `get_map_detail` 的 `bid_list` 参数用法待进一步探索
- L0 执行器已支持 7 种指令: MOVE_CITY, ATTACK_TARGET, SCOUT, GARRISON_BUILDING, INITIATE_RALLY, JOIN_RALLY, RETREAT

---

## Phase 2: 单小组验证

> L1 Prompt 调试 + L0 校验器 + JSON 输出稳定性

### 已完成

| 组件 | 文件 | 提交 | 说明 |
|------|------|------|------|
| **LLM 集成** | `src/ai/llm_client.py` | `38ad415` | ZhiPu GLM 接入，LLM 凭证移至 gitignored `llm_secret.yaml` |
| **L1 局部视图** | `src/perception/l1_view.py` | `38ad415` | 307行，小队视角构建，敌方/建筑按距离排序（top 20/15） |
| **L1 小队队长** | `src/ai/l1_leader.py` | `38ad415` | 170行，L1Leader + L1Coordinator 并行小队决策 |
| **L1 战术规则** | `src/ai/prompts/l1_system.txt` | `23faa82` | 修订为2出征槽位 + 英雄互斥规则 |
| **LLM 凭证安全** | `config/llm_secret.yaml` | `87c7d75` | 凭证 gitignored，缺失时 graceful fallback |
| **Account→PlayerState** | `src/models/account.py` | `c9a468c` | 重命名消除与 config/accounts.yaml 歧义 |
| **集结协议修正** | `src/executor/game_api.py` | `8ef2b4c` | create_rally + join_rally 参数对齐真实客户端协议 |
| **rally_dismiss** | `src/executor/game_api.py` | `e25a889` | 新增集结解散命令，rally 生命周期完整 |
| **集结集成测试** | `test_rally.sh` | `10e5745` | 端到端: 补兵→移城→侦察→发起集结→加入→等待→伤亡验证 |
| **40人双阵营** | `config/accounts.yaml` | `a8d4ca1` | 20 AI + 20 敌方，双联盟对抗配置 |
| **协议扩充至30** | `src/config/cmd_config.yaml` | `19d0908` | +13个命令: 联盟(4) + AVA(3) + GM(5) + 召回(1)，param_overrides 修复 |

| **L0 ActionType 补全** | `src/executor/l0_executor.py` | `19d0908` | 9种完整ActionType: 含 RALLY_DISMISS + RECALL_REINFORCE，validate/dispatch/message 三处均覆盖 |
| **建筑 target_type 修复** | `src/executor/game_api.py` | — | attack_building/reinforce_building/create_rally 自动从 building_id 提取 target_type（修复 30001 错误） |
| **LLM 429 退避重试** | `src/ai/llm_client.py` | — | 速率限制时指数退避（2^n × 3s），避免连续调用耗尽配额 |
| **LLM 超时调优** | `config/system.yaml` | — | timeout 60→120s, retries 1→2, 适配 GLM-4.5-Air 响应时间 |
| **L1 实战测试** | `test_l1_live.sh` | — | 6项端到端测试: LLM连通→单队决策→JSON校验→3轮稳定性→主循环→4队覆盖, 13/14 PASS |
| **LLM JSON 稳定性** | — | — | GLM-4.5-Air 3/3轮 100% JSON解析成功, 4/4小队覆盖 |

### 待完成

| 组件 | 文件 | 说明 |
|------|------|------|
| L1 Prompt 迭代 | `src/ai/prompts/l1_system.txt` | 基于实战测试结果持续调优（当前中立建筑→solo攻击决策合理） |

---

## Phase 3: 多组并发 + L2

> 10组并行 + L2 开发 + 记忆模块 + 管理员 CLI

### 已完成

| 组件 | 文件 | 提交 | 说明 |
|------|------|------|------|
| **L2 全局视图** | `src/perception/l2_view.py` | `034c02c` | 467行，5个Pydantic模型 + L2ViewBuilder（DBSCAN敌方聚类 eps=150，建筑分类，战力加权中心，markdown格式化） |
| **L2 系统提示词** | `src/ai/prompts/l2_system.txt` | `034c02c` | 输入数据格式说明 + JSON输出schema（thinking + orders数组） |
| **L2 视图单元测试** | `tests/test_l2_view.py` | `034c02c` | 25个测试: 小队聚合(5) + DBSCAN聚类(8) + 建筑分类(4) + 全局指标(4) + 格式化(2) + 边界(2) |
| **pytest 测试基础设施** | `tests/conftest.py` | `034c02c` | integration/slow marker + session-scoped mock_server fixture |
| **集成测试包装** | `tests/test_integration_mock.py` | `034c02c` | 6个集成测试: 3 PASS + 3 xfail，shell脚本→pytest subprocess包装 |
| **L2 军团指挥官** | `src/ai/l2_commander.py` | `c24bd2e` | ~100行，接收L2GlobalView→LLM调用→容错解析为dict[int,str]，复用L2ViewBuilder |
| **主循环接入 L2** | `src/controller/loop.py` | `c24bd2e` | Phase 2 stub→真实L2Commander调用，l2_orders传递给L1Coordinator |
| **L2 Commander 单元测试** | `tests/test_l2_commander.py` | `c24bd2e` | 5个async测试: 正常解析/缺失小队/非法ID/空response(dry_run)/thinking日志 |

### 待完成

| 组件 | 文件 | 说明 |
|------|------|------|
| 记忆模块 | `src/ai/memory.py` | 最近5轮上下文 + 历史压缩 |
| 管理员 CLI | `src/controller/admin_cli.py` | 自然语言实时干预 |
| L2+L1 联合实战测试 | — | 端到端: L2战略→L1战术→L0执行 全链路验证 |

### 前置条件

- Phase 2 单组验证通过 ✅

---

## Phase 4: 实战调优

> 对抗测试 + 参数调优 + 移城策略优化

### 待完成

| 组件 | 说明 |
|------|------|
| 对抗测试 | AI vs 真人玩家实战 |
| 参数调优 | 行军阈值、集结人数、撤退条件等 |
| 移城策略 | 利用"移城无CD"的核心战术优化 |
| Mock 对战 | AI vs Mock 敌方AI |
| 日志分析 | JSON 日志回放与复盘 |

### 前置条件

- Phase 3 多组并发稳定运行

---

## 总体进度

```
Phase 1 ████████████████████ 100%   基础设施 ✅
Phase 2 ██████████████████░░  90%   单小组验证 (实战通过，Prompt待持续调优)
Phase 3 ███████████████░░░░░  60%   多组并发+L2 (L2Commander+主循环+联合测试)
Phase 4 ░░░░░░░░░░░░░░░░░░░░  0%   实战调优
```

## 关键里程碑

- [x] 端到端通路: CLI → GameAPI → Test Server（2026-03-09）
- [x] Pydantic 数据模型 + 服务端响应采集（2026-03-10）
- [x] P0 配置系统: schemas + loader + 4个 YAML（2026-03-10）
- [x] L0 执行器: 7种AI指令翻译+校验 + 集成测试（2026-03-11）
- [x] 数据同步: 并发账号+地图同步 + 集成测试10/10通过（2026-03-11）
- [x] 主循环: AIController 5阶段编排 + Phase 1 验收全部通过（2026-03-11）
- [x] Phase 2 核心: LLM集成(GLM) + L1视图 + L1决策引擎（2026-03-11）
- [x] 集结全流程: create→join→dismiss 在 test server 验证通过（2026-03-12）
- [x] 协议扩充: 18→30命令字 + 40人双阵营对抗配置（2026-03-13）
- [x] 单组 L1 首次自主实战决策: GLM-4.5-Air, 4/4小队通过, 13/14测试PASS（2026-03-17）
- [x] 建筑 target_type 修复: attack/reinforce/rally 自动提取, 30001→0（2026-03-17）
- [x] L2 全局视图: DBSCAN聚类 + 建筑分类 + 25单元测试全通过（2026-03-17）
- [x] pytest 测试基础设施: 28 passed (1m21s), integration/slow markers（2026-03-17）
- [x] L2 军团指挥官 + 主循环接入: L2Commander→LLM→dict + loop.py Phase 2 接入（2026-03-17）
- [x] L2+L1 联合实战测试: test_l2_l1_integration.sh 7项测试脚本（2026-03-19）
- [ ] 首场 AI vs 真人对战

---

## 下一步行动（推荐顺序）

### 当前阶段：Phase 3 推进中

#### ~~已完成~~

1. ~~**L2 全局视图 `l2_view.py`** ✅~~ — DBSCAN聚类 + 建筑分类 + 25单元测试
2. ~~**pytest 测试基础设施** ✅~~ — conftest + integration/slow markers + 1m21s回归
3. ~~**L2 军团指挥官 `l2_commander.py`** ✅~~ — LLM调用 + 容错解析 + 5个单元测试
4. ~~**主循环接入 L2** ✅~~ — Phase 2 stub→真实调用，l2_orders→L1Coordinator

#### ~~已完成~~

5. ~~**L2+L1 联合实战测试** ✅~~ — `test_l2_l1_integration.sh` 7项测试: L2单独决策/指令传递/日志结构/多轮稳定性/指令完整性/自然语言质量

#### 下一步（推荐顺序）

6. **记忆模块 `memory.py`** ← 当前最高优先级
   - 最近 5 轮上下文保持 + 历史压缩
   - L2 层面: 上一轮 orders + 执行结果摘要
   - L1 层面: 最近指令 + 部队行动结果

7. **管理员 CLI `admin_cli.py`**
   - 自然语言实时干预（如: "全军集中攻击据点27_4_1"）
   - 注入到 L2 prompt 的 admin_intent 字段

8. **L2 指令日志增强**
   - 在 `logs/loop_*.json` 中记录 L2 的原始 orders（便于调试指令传递）
   - 在 `LoopStats` 中添加 `l2_orders` 字段
