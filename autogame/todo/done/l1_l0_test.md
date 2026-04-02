## 目标
测试 L1+L0完整决策+执行链路
完成 L1 在 test server 上的ava战场实战测试，生成对应的l0指令并执行。
接受以下l1指令
"[小队 1 (Alpha)] 控制 建筑 pos:( 154, 170 )"
在test环境上完成以下任务

## 架构设计决策（已确认）
- **L1 决策方式**：生成多个不同的 prompt 模板，允许通过 `--l1-prompt` 参数切换
  - `l1_system.txt` - 主世界通用版本
  - `l1_system_ava.txt` - AVA 战场专用版本（使用 LVL_* 指令）
  - `l1_system_ava_test.txt` - AVA 测试专用版本（内置固定逻辑，无需 LLM）
- **目标建筑**：`10006_1773137411102403` at pos:(154, 170)，AVA 地图中的佣兵营
- **AVA 战场 ID**：`lvl_id=29999`
- **AVA 地图同步**：DataSyncer 支持 `--ava <lvl_id>` 参数，使用 `lvl_battle_login_get` API
- **LLM 切换**：`--llm <profile>` 全局参数，支持 zhipu / ollama

## 已完成工作项

### [x] 1. Prompt 模板系统
- [x] 创建 `src/ai/prompts/l1_system_ava.txt` - AVA 战场专用 prompt
- [x] 创建 `src/ai/prompts/l1_system_ava_test.txt` - 测试专用 prompt
- [x] 修改 `L1Leader.__init__()` 支持 `prompt_template` 参数
- [x] 修改 `L1Coordinator.__init__()` 支持 `prompt_template` 参数
- [x] 修改 `cmd_run()` 添加 `--l1-prompt <name>` 参数

### [x] 2. Mock L2 支持
- [x] 修改 `cmd_run()` 添加 `--mock-l2 "<指令>"` 参数
- [x] 修改 `AIController.__init__()` 接受 `mock_l2` 参数
- [x] 修改 `AIController._run_one_loop()` Phase 2 使用 mock_l2
- [x] 添加 `AIController._parse_mock_l2()` 解析指令

### [x] 3. 坐标与建筑 ID 处理
- [x] 添加 `parse_target_coordinates()` 解析 L2 指令中的坐标
- [x] 添加 `find_building_by_pos()` 查找指定坐标的建筑
- [x] 添加 `get_building_control_status()` 获取建筑控制状态

### [x] 4. 准备脚本
- [x] 创建 `scripts/prepare_alpha.sh` - AVA 战场准备脚本
- [x] 创建 `scripts/run_ava_test.sh` - 测试运行脚本

### [x] 5. 验收标准日志输出
- [x] 添加 `AIController._print_acceptance_log()` 打印验收日志
- [x] 每循环打印队员位置
- [x] 每循环打印目标建筑控制状态
- [x] 添加"建筑被本联盟控制"检测提示

### [x] 6. DataSyncer AVA 战场地图支持
- [x] `data_sync.py`: 新增 `_sync_map_ava()` 方法，使用 `lvl_battle_login_get` API
- [x] `data_sync.py`: AVA 类型常量 (10101=玩家, 10000-10006=建筑, 10300=资源)
- [x] `building.py` / `enemy.py`: `from_brief_obj` 兼容 AVA 扁平格式 (camp/id 回退)
- [x] `loop.py`: AIController 透传 `lvl_id` 到 sync 阶段
- [x] `main.py`: `sync` / `l1_view` / `l1_decide` / `run` 命令添加 `--ava <lvl_id>` 参数
- [x] 修复 AVA 响应 push_list 遍历（数据在 push_list[2] 而非 [0]）
- [x] 修复 AVA 玩家 UID 提取（uid 字段为 0，实际 UID 在 id 字段）

### [x] 7. LLM 调用改进
- [x] `main.py`: 添加 `--llm <profile>` 全局参数切换 LLM (zhipu/ollama)
- [x] `main.py`: `l1_decide` / `l2_decide` 自动打印完整 prompt 和 LLM 响应
- [x] `main.py`: `--help` 输出改用 docstring + 补充说明
- [x] `llm_client.py`: 所有 LLM 统一流式输出到 stderr，实时可见
- [x] `llm_client.py`: Ollama 改用原生 `/api/chat` + `think=false` + `num_ctx=16384`
  - 解决 `/v1/` 兼容端点不转发 think 参数导致 qwen3.5 卡在 thinking 的问题

### [x] 8. 集成测试验证
- [x] `sync --ava 29999`: 11 AVA 建筑 + 1 敌方，目标 (154,170) 可见
- [x] `l1_view 1 --ava 29999`: L1 视图包含 AVA 建筑，按距离排序
- [x] `l1_decide 1 --ava 29999 --mock-l2 ...`: L1 生成正确的 LVL_ATTACK_BUILDING 指令
- [x] `run --once --ava 29999 --mock-l2 ...`: 全链路 Sync→L2→L1→L0 跑通
  - Squad 1 (uid 643-647) 成功移城到目标附近并发起攻击
  - Squad 2-4 失败 (code=30001，未进入 AVA 战场)
  - 目标建筑占领倒计时中（游戏机制）

## 待处理
- [ ] Squad 2-4 的账号需要用 `uid_ava_enter` 进入 AVA 战场后才能执行指令
- [ ] 多轮循环测试：验证占领倒计时结束后建筑归属变更
- [ ] Ollama (qwen3.5:4b) 作为 L1 的 JSON 输出稳定性验证

## 测试命令

### 数据同步验证
```bash
# AVA 地图同步（查看建筑列表）
python src/main.py sync --ava 29999

# L1 视图（查看小队局部视图）
python src/main.py l1_view 1 --ava 29999
```

### L1 决策调试（自动打印完整 prompt + response）
```bash
# 使用 zhipu (默认)
python src/main.py l1_decide 1 --ava 29999 \
  --mock-l2 "[小队 1 (Alpha)] 控制 建筑 pos:( 154, 170 )" \
  --l1-prompt ava

# 使用 ollama
python src/main.py --llm ollama l1_decide 1 --ava 29999 \
  --mock-l2 "[小队 1 (Alpha)] 控制 建筑 pos:( 154, 170 )" \
  --l1-prompt ava

# 使用测试专用 prompt（内置固定逻辑）
python src/main.py --llm ollama l1_decide 1 --ava 29999 \
  --mock-l2 "[小队 1 (Alpha)] 控制 建筑 pos:( 154, 170 )" \
  --l1-prompt ava_test

# dry-run 模式（不调用 LLM）
python src/main.py l1_decide 1 --ava 29999 --dry-run --json
```

### 全链路测试
```bash
# 单轮全链路 (Sync → L2 mock → L1 LLM → L0 执行)
python src/main.py run --once --loop.interval_seconds 0 --ava 29999 --mock-l2 "[小队 1 (Alpha)] 控制 建筑 pos:( 154, 170 )" --l1-prompt ava_test

# 多轮持续运行
python src/main.py run --ava 29999 \
  --mock-l2 "[小队 1 (Alpha)] 控制 建筑 pos:( 154, 170 )" \
  --l1-prompt ava

# 使用 ollama 跑全链路
python src/main.py --llm ollama run --once --loop.interval_seconds 0 --ava 29999 --mock-l2 "[小队 1 (Alpha)] 控制 建筑 pos:( 154, 170 )"   --l1-prompt ava_test
```

### 脚本方式
```bash
# 准备 AVA 战场（添加成员到名单 + 进入战场）
bash scripts/prepare_alpha.sh 1 1

# 运行测试
bash scripts/run_ava_test.sh 154 170 ava
```

### L0 单条指令调试
```bash
# AVA 移城
python src/main.py l0 LVL_MOVE_CITY 20010643 154 170

# AVA 攻击建筑
python src/main.py l0 LVL_ATTACK_BUILDING 20010643 10006_1773137411102403 154 170

# AVA 攻击建筑（指定兵种）
python src/main.py l0 LVL_ATTACK_BUILDING 20010643 10006_1773137411102403 154 170 --soldier 204 3000
```

## 验收标准
- [x] python src/main.py run 进程持续运行不退出
- [x] 每循环打印所有队员的位置，还有该建筑被哪个联盟所控制
- [x] Squad 1 成员成功移城到目标建筑附近并发起攻击
- [ ] 数个loop之后，最终应打印出该建筑被本联盟控制（占领倒计时中）

## 进度跟踪
- 状态：集成测试基本通过，占领倒计时验证中
- 开始时间：2026-03-19
- 最后更新：2026-03-23
