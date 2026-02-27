# Auto Loop 自动循环模式

启动方式：

```bash
python main.py --auto              # 无限循环
python main.py --auto --loops 50   # 限制最多 50 轮
```

`auto_loop` 是一个无限循环（或受 `--loops` 限制），每次迭代执行以下决策链。按 `Ctrl+C` 可优雅退出并保存状态。

## 每次循环执行流程（按优先级排序）

| 步骤 | 操作 | 说明 |
|------|------|------|
| **0. ADB 健康检查** | 检测模拟器连接，断开则自动重连 | 最多重试 `ADB_RECONNECT_RETRIES`(3) 次，失败则停止循环 |
| **1. 截图** | `screenshot_mgr.capture()` | 连续 3 次截图失败触发 ADB 重连 |
| **2. 场景分类** | `classifier.classify(screenshot)` | 识别当前画面属于哪种场景（见下方场景列表） |
| **2a. 卡死检测** | 连续 `STUCK_MAX_SAME_SCENE`(10) 次相同场景触发恢复 | 逐步升级：按返回 → 点击中心 → 重启游戏 |
| **2c. 主城状态更新** | 在主城场景下提前提取任务栏信息 | 为后续手指检测和任务触发提供数据 |
| **2d. 教程手指检测** | 检测画面中的"引导手指"图标 | **最高优先级**，发现就直接点击手指尖位置；若在主城任务栏上检测到手指，可快速启动 quest workflow 直接进入 EXECUTE_QUEST 阶段 |
| **3. 退出对话** | `exit_dialog` → 点击"继续"按钮 (826, 843) | 暗背景容易被误判为其他场景，优先处理；点击后等待 60s |
| **3b. 英雄列表/招募** | `hero` → 点返回；`hero_recruit` → 先点 primary button 再返回 | 防止卡在英雄界面 |
| **3c. 英雄升级** | `hero_upgrade` → 有红字（资源不足）不点升级，直接返回 | 使用 `has_red_text_near_button()` 检测资源不足 |
| **4. 弹窗处理** | `popup` 场景（quest workflow 未激活时）→ 先检查奖励按钮 → 关闭弹窗 | 跳过弹窗，不让弹窗阻塞流程 |
| **4b. 剧情对话** | `story_dialogue` → 尝试点"跳过" → 点三角 → 点屏幕中心 | 自动跳过剧情 |
| **5. 加载画面** | `loading` → 检查是否有 primary button（防止误判）→ 等待 | 真正的加载画面不做操作，只等待 |
| **5b. 任务工作流** | `quest_workflow` 激活中 → 执行工作流状态机 | 任务脚本驱动的多步操作（见下方状态机详述） |
| **6. 未知场景** | 尝试 primary button → 3 次未知则按返回 → 尝试弹窗关闭 → LLM 分析 | 防止卡在未知界面 |
| **7. 状态更新** | 非主城场景的 `state_tracker.update()` | 主城在步骤 2c 已更新 |
| **7.5 任务栏触发** | 主城 + 任务栏可见 + `should_start()` = true → 启动 quest workflow | 自动识别并执行任务栏显示的当前任务 |
| **8. 三层决策** | 核心逻辑，三选一（见下方详述） | |
| **9. 持久化** | 保存游戏状态到 `data/game_state.json` | 每次迭代结束时 |
| **10. 日志** | 每 10 轮输出状态摘要，每 20 轮清理已完成任务 | |

每次迭代最后 `sleep(LOOP_INTERVAL)` (2.0s) 后进入下一轮。

## 场景类型

场景分类采用优先级瀑布检测（`SceneClassifier.classify()`）：

| 优先级 | 场景 | 检测方式 |
|--------|------|----------|
| 1 | `popup` | 屏幕边缘比中心暗（暗遮罩），且匹配到关闭/X 按钮模板 |
| 2 | `exit_dialog` | 匹配 `scenes/exit_dialog` 模板（暗背景+蓝色图标） |
| 3 | `loading` | 灰度标准差 <20（颜色均匀）或均值 <30/>240 |
| 4 | `story_dialogue` | `icons/down_triangle` 模板匹配 ≥0.9 |
| 5 | `main_city` / `world_map` | 裁剪右下角区域匹配 `scenes/` 下对应图标，阈值 ≥0.5 |
| 6 | `hero` / `hero_recruit` / `hero_upgrade` / `battle` | `scenes/` 目录全扫描匹配 |
| 7 | `unknown` | 兜底 |

## 三层决策（步骤 8）

这是 auto loop 的核心，三选一：

1. **有待办任务** → **规则引擎**（战术层）分解任务为具体操作并执行，响应时间 <500ms
2. **无任务 + LLM 咨询时间到**（间隔 `LLM_CONSULT_INTERVAL` = 1800s）→ **LLM 生成战略计划**（战略层），生成的任务加入队列
3. **无任务** → **auto_handler** 自动扫描当前画面寻找可做的事（机会主义行为，如收资源、领奖励）

90% 的操作由本地规则引擎和 CV 完成，LLM 只是定期咨询的"顾问"。

### 规则引擎支持的任务类型

`collect_resources`, `upgrade_building`, `train_troops`, `claim_rewards`, `navigate_main_city`, `navigate_world_map`, `close_popup`, `check_mail`, `collect_daily`

### AutoHandler 优先级

当没有待办任务且 LLM 未到咨询时间时，`AutoHandler.get_actions()` 按以下顺序扫描：

1. **已知弹窗** — 匹配标识模板，点击对应关闭模板
2. **奖励按钮** — 模板匹配 `buttons/claim` 等 + OCR 匹配"领取"等文字
3. **加载画面** — 点击屏幕中心

## Quest Workflow 状态机（步骤 5b / 7.5）

当任务栏有可执行的任务时，系统会暂停 LLM 排的任务队列，优先执行游戏主线/支线任务。

### 状态流转

```
IDLE → ENSURE_MAIN_CITY → READ_QUEST → CLICK_QUEST → EXECUTE_QUEST
     → RETURN_TO_CITY → CHECK_COMPLETION → CLAIM_REWARD → VERIFY → IDLE
```

### 各阶段说明

| 阶段 | 行为 |
|------|------|
| **ENSURE_MAIN_CITY** | 不在主城时尝试返回：OCR "城池"/"主城" → `buttons/back_arrow` → 点击空白区域；若在 popup 场景则跳至 EXECUTE_QUEST |
| **READ_QUEST** | 检测任务栏文字，记录 `target_quest_name`；若已有绿色对勾则跳至 CLAIM_REWARD |
| **CLICK_QUEST** | 点击任务栏文字区域中心，进入 EXECUTE_QUEST |
| **EXECUTE_QUEST** | 核心执行阶段（见下方详述），最多 `max_execute_iterations`(40) 轮 |
| **RETURN_TO_CITY** | 执行完毕或超时后返回主城 |
| **CHECK_COMPLETION** | 检查任务栏是否有绿色对勾 |
| **CLAIM_REWARD** | 点击任务栏领取奖励 |
| **VERIFY** | 验证任务文字已变化（新任务出现），完成后回到 IDLE |

### EXECUTE_QUEST 阶段详细逻辑

EXECUTE_QUEST 是最复杂的阶段，按场景分支处理：

**popup 场景** — 多阶段弹窗消除：
1. OCR 匹配消除文字（"确定"、"领取"等）
2. `close_x` 模板关闭
3. 教程手指检测
4. OCR 匹配动作按钮（"建造"、"升级"等）
5. `find_primary_button()` 颜色检测
6. 逐步升级：返回箭头 → 中心点击 → LLM 分析

**story_dialogue** — 尝试"跳过"，然后点三角

**main_city（无手指）** — 推进到 CHECK_COMPLETION

**通用流程**：
1. `_match_quest_rule()` 匹配 JSON quest 脚本执行
2. OCR 匹配动作按钮（有**按钮疲劳机制**：同一按钮连续点击 2 次后标记为 exhausted，跳过）
3. `find_primary_button()` 颜色检测（HSV，蓝/绿优先，金色次之）
4. 所有按钮 exhausted → RETURN_TO_CITY
5. 尝试 `close_x` 关闭全屏弹窗
6. LLM 分析（如果配置了）
7. 兜底：点击屏幕中心

### 教程手指快速通道

教程手指（tutorial finger）检测优先级高于一切。在主城检测到手指位于任务栏区域时，可跳过 ENSURE_MAIN_CITY / READ_QUEST / CLICK_QUEST，直接快速启动 quest workflow 进入 EXECUTE_QUEST。

### Abort Cooldown

如果任务被中止（超时、exhausted 等），`_ABORT_COOLDOWN = 180s`（3 分钟）内 `should_start()` 会阻止重启同一任务，防止反复失败。

## Primary Button 检测

`find_primary_button()` 基于 HSV 颜色检测可点击按钮，不依赖模板或 OCR：

| 优先级 | 颜色 | 用途 |
|--------|------|------|
| 高 | 蓝色 / 绿色 | 主要动作按钮（升级、确认等） |
| 低 | 金色 | 次要按钮 |

配合 `has_red_text_near_button()` 可检测按钮附近是否有红色文字（资源不足提示），避免无效点击。

## 卡死恢复

`StuckRecovery` 在连续 `STUCK_MAX_SAME_SCENE`(10) 次相同场景时触发，逐步升级：

| 等级 | 操作 | 说明 |
|------|------|------|
| Level 1 | `key_event(4)` — 按返回键 | 最温和的退出方式 |
| Level 2 | `tap(center_x, center_y)` — 点击屏幕中心 | 尝试关闭可能的遮挡 |
| Level 3 | `force-stop` + `monkey` 重启游戏 | 最后手段 |

场景变化时调用 `reset()` 重置等级回 0。恢复后清空 `scene_history`。

## 容错机制

| 异常情况 | 处理策略 |
|---------|---------|
| **ADB 断连** | 自动重连，最多重试 `ADB_RECONNECT_RETRIES`(3) 次 |
| **截图失败** | 连续 3 次后触发 ADB 重连 |
| **卡死检测** | 连续相同场景时逐步升级恢复手段（返回 → 中心点击 → 重启） |
| **连续异常** | 5 次连续 Python 异常则终止循环 |
| **Ctrl+C** | 优雅退出，保存游戏状态 |

## 关键配置参数

| 常量 | 值 | 用途 |
|------|---|------|
| `LOOP_INTERVAL` | 2.0s | 迭代间隔 |
| `LLM_CONSULT_INTERVAL` | 1800s | LLM 咨询频率 |
| `STUCK_MAX_SAME_SCENE` | 10 | 触发卡死恢复的相同场景次数 |
| `ADB_RECONNECT_RETRIES` | 3 | ADB 重连最大次数 |
| `ACTION_MAX_RETRIES` | 3 | 单个 action 执行重试次数 |
| `SCREEN_WIDTH / HEIGHT` | 1080 × 1920 | 模拟器分辨率要求 |
| `max_execute_iterations` | 40 | EXECUTE_QUEST 阶段最大迭代数 |
| `_ABORT_COOLDOWN` | 180s | 任务中止后冷却时间 |
| `_ACTION_BUTTON_EXHAUST_THRESHOLD` | 2 | 按钮疲劳阈值（连续点击次数） |

## 相关代码

- 主循环：`main.py` — `GameBot.auto_loop()`
- 场景分类：`scene/classifier.py` — `SceneClassifier.classify()`
- 弹窗过滤：`scene/popup_filter.py` — `PopupFilter.handle()`
- Primary Button：`scene/classifier.py` — `find_primary_button()` / `has_red_text_near_button()`
- 规则引擎：`brain/rule_engine.py` — `RuleEngine.plan()`
- LLM 规划：`brain/llm_planner.py` — `LLMPlanner.get_plan()`
- 自动处理：`brain/auto_handler.py` — `AutoHandler.get_actions()`
- 任务工作流：`brain/quest_workflow.py` — `QuestWorkflow.step()`
- 卡死恢复：`brain/stuck_recovery.py` — `StuckRecovery.check()` / `recover()`
- 执行管线：`executor/` — `ActionValidator` → `ActionRunner` → `ResultChecker`
