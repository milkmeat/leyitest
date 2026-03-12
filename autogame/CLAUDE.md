# WestGame AI 全自动化团战系统

## 项目概述

AI 控制 100 个 NPC 账号（每账号最多2支出征部队，共200个行动单元）在 SLG 手游团战副本中自动对战真人玩家。
采用递归分层指挥体系：L2(战略) → L1×10(战术,并行) → L0(执行,代码层)。

- **需求文档**: `WestGame_AI团战系统需求规格说明书v2.md`（唯一需求来源）
- **命令字配置**: `cmd_config.yaml`（游戏服务器 HTTP 命令字最小集合）
- **接口协议**: `gg后台接口协议.md`（后台接口完整协议）

## 技术栈

- Python 3.11+, asyncio, aiohttp, Pydantic v2, PyYAML
- Mock Server: FastAPI + uvicorn
- LLM: 待定（需要 thinking/reasoning + JSON 输出能力）

## 目录结构

```
autogame/
├── src/                        # 主系统源码
│   ├── main.py                 # 入口，启动主循环
│   ├── config/                 # 配置加载与校验
│   │   ├── loader.py           #   YAML 加载器
│   │   └── schemas.py          #   Pydantic 配置 schema
│   ├── models/                 # 数据模型 (Pydantic)
│   │   ├── account.py          #   Account + Troop
│   │   ├── building.py         #   Building (据点)
│   │   ├── enemy.py            #   Enemy (敌方玩家)
│   │   ├── rally.py            #   Rally (集结)
│   │   └── score.py            #   Score (积分)
│   ├── controller/             # 控制层
│   │   ├── loop.py             #   AIController 60秒主循环
│   │   └── admin_cli.py        #   管理员 CLI
│   ├── ai/                     # AI 决策层
│   │   ├── l2_commander.py     #   L2 军团指挥官 (1个LLM)
│   │   ├── l1_leader.py        #   L1 小队队长 (10个LLM并行)
│   │   ├── memory.py           #   上下文/历史记忆管理
│   │   └── prompts/            #   LLM Prompt 模板
│   │       ├── l2_system.txt
│   │       └── l1_system.txt
│   ├── executor/               # L0 执行层
│   │   ├── l0_executor.py      #   指令翻译 + 校验
│   │   └── game_api.py         #   游戏服务器 HTTP 客户端
│   └── perception/             # 数据感知层
│       ├── data_sync.py        #   原始数据获取
│       ├── l1_view.py          #   L1 局部视图构建
│       └── l2_view.py          #   L2 全局摘要构建 (含DBSCAN聚类)
├── mock_server/                # Mock 游戏服务器
│   ├── app.py                  #   FastAPI 应用 (POST /api/game)
│   ├── world_state.py          #   内存世界状态
│   ├── simulation.py           #   Tick 驱动模拟引擎
│   ├── battle.py               #   战斗结算
│   ├── enemy_ai.py             #   敌方脚本 AI
│   └── fixtures/               #   测试场景预设 (YAML)
├── config/                     # 运行时配置 (YAML)
│   ├── accounts.yaml           #   100个账号配置
│   ├── squads.yaml             #   10个小组分配
│   ├── activity.yaml           #   活动规则
│   └── system.yaml             #   系统参数
├── tests/                      # 测试
├── logs/                       # 运行日志 (gitignored)
├── requirements.txt
└── .gitignore
```

## 核心架构

### 指挥层级

| 层级 | 角色 | 实现 | 管理对象 | 刷新频率 |
|------|------|------|---------|---------|
| L2 | 军团指挥官 | 1个LLM | 10个L1小队 | 1-3分钟 |
| L1 | 小队队长 | 10个LLM(并行) | 10账号×2出征=20单元 | 1分钟 |
| L0 | 执行层 | Python代码 | HTTP命令字 | 实时 |

### 主循环 (60秒)

```
Phase 1: Sync (0-5s)     — asyncio.gather 并发查询100账号+全图
Phase 2: L2 (5-15s)      — 单次LLM调用，生成10条战略指令
Phase 3: L1 (15-45s)     — 10个LLM并行，生成具体行动指令
Phase 4: Action (45-55s) — 流水线发送HTTP（生成即发送）
Phase 5: Sleep (55-60s)  — 等待下一轮
```

### AI 指令 → 游戏命令字映射

| AI 指令 | 游戏命令字 | 说明 |
|---------|-----------|------|
| MOVE_CITY | fixed_move_city_new | 移城（瞬移+全军召回） |
| ATTACK_TARGET | dispatch_troop | 攻击玩家/建筑 |
| SCOUT | dispatch_scout | 即时侦察 |
| GARRISON_BUILDING | dispatch_troop (march_type:11) | 驻防据点 |
| INITIATE_RALLY | create_rally_war | 发起集结 |
| JOIN_RALLY | 待确认 | 加入集结 |
| RETREAT | change_troop (march_type:5) | 召回部队 |

## 关键游戏机制（开发必读）

1. **移城无CD**：最强战术操作，瞬移+全军秒回+重新部署
2. **2出征槽位系统**：每账号最多派出2支部队出征（1 solo + 1 rally队员，或纯2 solo；rally队长因英雄占用只能出1支）。未出征部队自动守城
3. **兵种克制**: archer > infantry > cavalry > archer（三角克制，系数1.3/0.7）
4. **集结**: 5分钟窗口，队长发起后队员加入，战斗用队长的英雄/科技，上限15人
5. **行军**: 2秒/格，100格≈200秒。有加速道具
6. **无战争迷雾**: 可实时获取所有敌方信息
7. **伤兵不可恢复**: 2小时副本内被击败=永久损失

## 编码规范

- 数据模型用 Pydantic v2（自带序列化/校验）
- 异步用 asyncio，并发查询/LLM调用用 `asyncio.gather(return_exceptions=True)`
- LLM 超时控制: `asyncio.wait_for(timeout=30)`
- 配置文件用 YAML，运行时全在内存
- 日志按 loop 编号组织为 JSON 文件
- 所有异常延迟到下一 loop 处理，不做实时重试
- L0 校验: 坐标 0-999，部队状态检查，UID 合法性

## 开发路线图

1. **Phase 1 基础设施**: Mock Server + Pydantic 数据模型 + 主循环骨架 + 配置加载
2. **Phase 2 单小组验证**: L1 Prompt调试 + L0 校验器 + JSON输出稳定性
3. **Phase 3 多组并发+L2**: 10组并行 + L2开发 + 记忆模块 + 管理员CLI
4. **Phase 4 实战调优**: 对抗测试 + 参数调优 + 移城策略优化

## 待确认项

详见需求规格说明书 §11。主要包括：完整命令字列表、积分计算公式、地图建筑布局、集结加入命令字等。
