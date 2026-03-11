# WestGame AI 团战系统 — 开发进度

> 最后更新: 2026-03-11 (Phase 1 基础设施全部完成 ✅)

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

### 待完成

| 组件 | 文件 | 说明 |
|------|------|------|
| L1 小队队长 | `src/ai/l1_leader.py` | 单个 LLM 驱动10账号×3部队的战术决策 |
| L1 局部视图 | `src/perception/l1_view.py` | 构建小队可见范围内的战场视图 |
| LLM JSON 输出 | — | 确保 LLM 输出结构化 JSON 指令的稳定性 |
| L1 Prompt 迭代 | `src/ai/prompts/l1_system.txt` | 基于测试结果调优提示词 |

### 前置条件

- ~~L0 执行器~~ ✅ 已完成
- ~~Phase 1 的主循环骨架 + 数据同步~~ ✅ 已完成
- 需要选定 LLM Provider（当前 TBD）

---

## Phase 3: 多组并发 + L2

> 10组并行 + L2 开发 + 记忆模块 + 管理员 CLI

### 待完成

| 组件 | 文件 | 说明 |
|------|------|------|
| L2 军团指挥官 | `src/ai/l2_commander.py` | 全局战略决策，生成10条指令分发给L1 |
| L2 全局视图 | `src/perception/l2_view.py` | 全局摘要 + DBSCAN 敌方聚类 |
| 记忆模块 | `src/ai/memory.py` | 最近5轮上下文 + 历史压缩 |
| 管理员 CLI | `src/controller/admin_cli.py` | 自然语言实时干预 |
| 10组并行调度 | `src/controller/loop.py` | `asyncio.gather` 并行10个 L1 |

### 前置条件

- Phase 2 单组验证通过

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
Phase 2 ░░░░░░░░░░░░░░░░░░░░  0%   单小组验证
Phase 3 ░░░░░░░░░░░░░░░░░░░░  0%   多组并发+L2
Phase 4 ░░░░░░░░░░░░░░░░░░░░  0%   实战调优
```

## 关键里程碑

- [x] 端到端通路: CLI → GameAPI → Test Server（2026-03-09）
- [x] Pydantic 数据模型 + 服务端响应采集（2026-03-10）
- [x] P0 配置系统: schemas + loader + 4个 YAML（2026-03-10）
- [x] L0 执行器: 7种AI指令翻译+校验 + 集成测试（2026-03-11）
- [x] 数据同步: 并发账号+地图同步 + 集成测试10/10通过（2026-03-11）
- [x] 主循环: AIController 5阶段编排 + Phase 1 验收全部通过（2026-03-11）
- [ ] 单组 L1 首次自主决策
- [ ] 10组并行 + L2 指挥
- [ ] 首场 AI vs 真人对战

---

## 下一步行动（推荐顺序）

### Phase 2 启动 — 单小组验证

1. **选定 LLM Provider**（决策项）
   - 需要支持 structured output / JSON mode
   - 候选: Claude API, OpenAI API, 本地模型
   - 影响 L1/L2 的实现方式

2. **L1 局部视图 `l1_view.py`**
   - 将 data_sync 的全局数据裁剪为单小队视角
   - 生成 L1 LLM 的输入 prompt 数据

3. **L1 小队队长 `l1_leader.py`**
   - 单小队 LLM 决策实现
   - JSON 输出解析 + 错误重试
   - 与 L0 executor 对接
