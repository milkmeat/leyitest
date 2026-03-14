# Phase 6: Quest Workflow — Progress Report

## Overview

在 Phase 5 框架搭建和游戏适配基础上，实现完整的 Quest 执行生命周期。引入 **Workflow** 概念（跨迭代状态机），与现有 TaskQueue（单迭代简单任务）互不干扰地协同工作。

---

## 已完成

### 1. Quest Bar 检测器 (`vision/quest_bar_detector.py` — 新建)

- `QuestBarInfo` dataclass：封装检测结果（visible、scroll_icon、red_badge、quest_text、green_check、tutorial_finger）
- `QuestBarDetector` 类：
  - 模板匹配 `icons/task_scroll` 定位卷轴图标
  - Y 坐标范围校验（82%-92% 屏幕高度）
  - HSV 颜色分析检测红色徽标（卷轴右上角，H:0-10/170-180, S>120, V>150）
  - OCR 读取卷轴右侧 quest 文本
  - HSV 颜色分析检测绿色对勾（quest 文本右侧，H:35-85, S>80, V>100）
  - 模板匹配 `icons/tutorial_finger`（缺失时优雅跳过）

### 2. Quest Workflow 状态机 (`brain/quest_workflow.py` — 新建)

`QuestWorkflow` 类，8 阶段状态机：

```
IDLE → ENSURE_MAIN_CITY → READ_QUEST → CLICK_QUEST → EXECUTE_QUEST
     → CHECK_COMPLETION → CLAIM_REWARD → VERIFY → IDLE
```

- 每次 `step(screenshot, scene)` 根据当前 phase 分发到对应处理方法，返回 action dicts
- `EXECUTE_QUEST` 阶段：优先跟随 tutorial_finger，回退到 LLM 分析，最后兜底点击屏幕中心
- `READ_QUEST` 阶段：红色徽标时优先点击卷轴领取待领奖励
- 安全保护：执行上限 20 次、完成检查重试 3 次、验证重试 3 次、quest bar 不可见时 abort

### 3. LLM Quest 执行分析 (`brain/llm_planner.py` — 修改)

- 新增 `QUEST_EXECUTION_PROMPT`：给 LLM 提供 quest 名称和截图，请求 1-5 个操作建议
- 新增 `analyze_quest_execution()` 方法：复用 `_call_vision_api()` 和 `_parse_scene_response()`

### 4. Game State 扩展 (`state/game_state.py` — 修改)

新增 7 个字段：
- Quest bar 状态（5 个）：`quest_bar_visible`、`quest_bar_has_red_badge`、`quest_bar_current_quest`、`quest_bar_has_green_check`、`quest_bar_has_tutorial_finger`
- Workflow 持久化（2 个）：`quest_workflow_phase`、`quest_workflow_target`
- `to_dict()` / `from_dict()` / `summary_for_llm()` 全部更新

### 5. State Tracker 集成 (`state/state_tracker.py` — 修改)

- 构造函数中创建 `QuestBarDetector` 实例
- `update()` 的 `main_city` 分支新增 `_update_quest_bar()` 调用

### 6. Auto Handler 扩展 (`brain/auto_handler.py` — 修改)

- `CLAIM_TEXT_PATTERNS` 增加 `"一键领取"`

### 7. Auto Loop 集成 (`main.py` — 修改)

- `GameBot.__init__()` 中创建 `QuestWorkflow` 实例
- Step 6.5：Workflow 活跃时优先执行 `workflow.step()`，跳过三层决策
- Step 7 else 分支：空闲且 quest bar 可见时自动启动 Workflow
- Step 3 popup 处理：关闭前先检查可领取奖励
- `cmd_status` 输出增加 quest bar 和 workflow 状态

### 8. 模板补充

- `icons/tutorial_finger.png` — 手指引导图标，已从游戏截图中截取

### 9. 测试 (`test_quest_workflow.py` — 新建)

35 个单元测试，全部通过：
- `TestQuestBarDetector`（8 个）：卷轴定位、Y 范围校验、OCR 文本读取、红色徽标、绿色对勾、手指图标检测及缺失处理
- `TestQuestWorkflow`（27 个）：所有阶段转移、重试上限、LLM 回退、game_state 同步、完整生命周期端到端测试

### 10. 文档 (`docs/workflow_complete_current_quest.md` — 更新)

添加自动触发条件、决策层优先级、安全保护、日志观察示例、测试说明

---

## 架构决策

### Workflow 与 TaskQueue 的关系

```
auto_loop 决策层（优先级从高到低）：
  popup/loading         → 现有处理
  Workflow 活跃         → workflow.step() 返回 actions
  TaskQueue 有任务      → rule_engine.plan() 返回 actions
  LLM 咨询              → llm_planner 生成任务加入 queue
  空闲 + 主城有 quest 栏 → 启动 Workflow
  空闲                  → auto_handler
```

- **Workflow**：跨迭代的状态机，管理有条件分支的复杂流程
- **TaskQueue**：单迭代完成的简单任务（LLM 生成或手动添加）
- 两者互不干扰：Workflow 活跃时优先执行；Workflow 空闲时 TaskQueue 正常工作

---

## 文件变更清单

| 文件 | 变更 |
|------|------|
| `vision/quest_bar_detector.py` | **新建** — QuestBarDetector + QuestBarInfo |
| `brain/quest_workflow.py` | **新建** — QuestWorkflow 状态机 |
| `brain/llm_planner.py` | 新增 QUEST_EXECUTION_PROMPT + analyze_quest_execution() |
| `state/game_state.py` | 新增 7 个 quest 相关字段，更新序列化 |
| `state/state_tracker.py` | 新增 QuestBarDetector 初始化 + _update_quest_bar() |
| `brain/auto_handler.py` | CLAIM_TEXT_PATTERNS 增加 "一键领取" |
| `main.py` | auto_loop 接入 Workflow + popup 领奖优先 + status 输出 |
| `templates/icons/tutorial_finger.png` | **新建** — 手指引导图标模板 |
| `test_quest_workflow.py` | **新建** — 35 个单元测试 |
| `docs/workflow_complete_current_quest.md` | 更新触发条件、优先级、安全保护、日志、测试说明 |

---

## 待验证

- [ ] `python main.py --auto --loops 30` 实际运行观察 quest workflow 日志
- [ ] 确认卷轴模板匹配在不同游戏状态下稳定
- [ ] 确认 OCR 能正确读取 quest 文本（中文）
- [ ] 确认红色徽标 / 绿色对勾 HSV 阈值在实际截图中准确
- [ ] 确认 tutorial_finger 模板匹配有效
- [ ] 测试 quest 执行完整循环（领取奖励后 quest 名称切换）
