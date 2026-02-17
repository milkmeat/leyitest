# Workflow: complete_current_quest

> 架构基础见 [workflow_design.md](workflow_design.md)
> 游戏 UI 说明见 [game_ui_description.md](game_ui_description.md)

## 目标

自动完成游戏 quest bar 中的当前 quest：读取 quest → 点击跳转 → 执行 → 检测完成 → 领取奖励 → 确认切换到下一个 quest。

**命名约定：** 游戏内的"任务"统一用 **quest**（quest_bar, current_quest 等），与系统内部的 task（TaskQueue, Task）区分。

## 自动触发条件

运行 `python main.py --auto --loops 30` 时，workflow 在三层决策的 `else` 分支自动启动（`main.py` step 7），需同时满足：

1. **scene == `"main_city"`** — 当前在主城
2. **`quest_bar_visible == True`** — `StateTracker` 在主城更新时检测到了卷轴图标
3. **`quest_bar_current_quest` 非空** — OCR 成功读取到 quest 文本
4. **TaskQueue 无待处理任务** 且 **LLM 咨询不到期**

一旦 `start()` 后，后续每次迭代都会在 step 6.5 优先执行 `quest_workflow.step()`，直到 workflow 回到 `IDLE`。

## 决策层优先级

```
auto_loop 决策层（优先级从高到低）：
  popup/loading         → 现有处理
  Workflow 活跃         → workflow.step() 返回 actions
  TaskQueue 有任务      → rule_engine.plan() 返回 actions
  LLM 咨询              → llm_planner 生成任务加入 queue
  空闲 + 主城有 quest 栏 → 启动 Workflow
  空闲                  → auto_handler
```

## 状态机

```
IDLE → ENSURE_MAIN_CITY → READ_QUEST → CLICK_QUEST → EXECUTE_QUEST → CHECK_COMPLETION → CLAIM_REWARD → VERIFY
  ↑                                         ↑            │  ↑               │                              │
  │                                         │       回到主城  超时回城        │ 无对勾                       │
  │                                         └────────────────────────────────┘                              │
  └────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

| 阶段 | 行为 | 转移条件 |
|------|------|----------|
| `IDLE` | 无操作 | auto_loop 空闲时启动 → `ENSURE_MAIN_CITY` |
| `ENSURE_MAIN_CITY` | 不在主城则导航回主城 | scene == main_city → `READ_QUEST` |
| `READ_QUEST` | 检测 quest bar，OCR 读取 quest 名称存入 `target_quest_name` | 有红色徽标 → 先点卷轴领奖；否则 → `CLICK_QUEST` |
| `CLICK_QUEST` | 点击 quest 文本跳转到执行入口 | 点击完成 → `EXECUTE_QUEST` |
| `EXECUTE_QUEST` | 手指图标 → 跟随点击；否则 → LLM 分析操作 | scene == main_city → `CHECK_COMPLETION`；超过上限 → 导航回城后 `CHECK_COMPLETION` |
| `CHECK_COMPLETION` | 检测 quest 文本右侧绿色对勾 | 有对勾 → `CLAIM_REWARD`；无对勾 → `CLICK_QUEST` 重试（有上限） |
| `CLAIM_REWARD` | 点击 quest 文本领取奖励 | → `VERIFY` |
| `VERIFY` | OCR 读取 quest 名称，确认已切换 | 名称变化 → `IDLE` |

## 涉及的文件

| 文件 | 改动 |
|------|------|
| `vision/quest_bar_detector.py` | **新建** — `QuestBarDetector` + `QuestBarInfo` |
| `brain/quest_workflow.py` | **新建** — `QuestWorkflow` 状态机类 |
| `brain/llm_planner.py` | 新增 `analyze_quest_execution()` 方法 + `QUEST_EXECUTION_PROMPT` |
| `state/game_state.py` | 添加 quest bar 状态字段 + workflow 执行状态字段 |
| `state/state_tracker.py` | 在 main_city 更新路径中调用 `_update_quest_bar()` |
| `brain/auto_handler.py` | 添加 `"一键领取"` 到 `CLAIM_TEXT_PATTERNS` |
| `main.py` | auto_loop 决策层接入 Workflow；popup 处理中增加领取奖励优先逻辑 |

## 实现细节

### 1. `vision/quest_bar_detector.py`（新文件）

**`QuestBarInfo` dataclass：**
- `visible: bool` — 是否检测到 quest bar
- `scroll_icon_pos: tuple[int, int] | None` — 卷轴图标中心坐标
- `scroll_icon_bbox: tuple[int, int, int, int] | None`
- `has_red_badge: bool` — 卷轴右上角红色数字徽标
- `current_quest_text: str` — 当前 quest 文本（OCR）
- `current_quest_bbox: tuple[int, int, int, int] | None` — quest 文本区域
- `has_green_check: bool` — quest 文本右侧绿色对勾
- `has_tutorial_finger: bool` — 手指引导图标
- `tutorial_finger_pos: tuple[int, int] | None`

**`QuestBarDetector` 类：**
- `__init__(template_matcher, ocr_locator)`
- `detect(screenshot) -> QuestBarInfo`：
  1. 模板匹配 `icons/task_scroll` 定位卷轴图标
  2. 验证卷轴 y 坐标在屏幕 82%-92% 范围内（~1574-1766px）
  3. 红色徽标：卷轴 bbox 右上象限 HSV 颜色分析（H:0-10 或 170-180, S>120, V>150, 阈值 50 像素）
  4. OCR 卷轴右侧区域获取 quest 文本
  5. **绿色对勾检测**：quest 文本 bbox 右侧区域 HSV 颜色分析（H:35-85, S>80, V>100, 阈值 30 像素）
  6. 模板匹配 `icons/tutorial_finger`（模板不存在时优雅跳过）

已有模板：`icons/task_scroll.png`。需后续捕获：`icons/tutorial_finger.png`。

### 2. `brain/quest_workflow.py`（新文件）

**`QuestWorkflow` 类**

```python
class QuestWorkflow:
    IDLE = "idle"
    ENSURE_MAIN_CITY = "ensure_main_city"
    READ_QUEST = "read_quest"
    CLICK_QUEST = "click_quest"
    EXECUTE_QUEST = "execute_quest"
    RETURN_TO_CITY = "return_to_city"
    CHECK_COMPLETION = "check_completion"
    CLAIM_REWARD = "claim_reward"
    VERIFY = "verify"
```

**构造函数参数：** `quest_bar_detector`, `element_detector`, `llm_planner`, `game_state`

**核心状态：**
- `phase: str` — 当前阶段
- `target_quest_name: str` — 启动时记录的 quest 名称
- `execute_iterations: int` — EXECUTE_QUEST 阶段的迭代计数
- `max_execute_iterations: int = 20` — 执行阶段最大迭代数，超过则放弃

**主方法 `step(screenshot, scene) -> list[dict]`：**
每次 auto_loop 调用，根据 `self.phase` 分发到 `_step_{phase}()` 方法，返回 actions 列表。

各阶段处理：

- **`_step_ensure_main_city(scene)`** — 如果 scene != main_city，返回导航动作（OCR 找"城池"/"home"，或 key_event BACK）。scene == main_city 时转移到 READ_QUEST。

- **`_step_read_quest(screenshot)`** — 调用 `quest_bar_detector.detect()`。如果 `has_red_badge`：优先走奖励领取流程（点卷轴 → 领取 → 返回）。否则记录 `target_quest_name = info.current_quest_text`，转移到 CLICK_QUEST。

- **`_step_click_quest(screenshot)`** — 检测 quest bar，点击 `current_quest_bbox` 中心。转移到 EXECUTE_QUEST，重置 `execute_iterations`。

- **`_step_execute_quest(screenshot, scene)`** — 核心执行逻辑：
  - 如果 scene == main_city → 转移到 CHECK_COMPLETION
  - 如果检测到手指图标（模板匹配） → 点击手指指向位置
  - 否则 → 调用 `llm_planner.analyze_quest_execution(screenshot, quest_name)` 获取动作建议
  - `execute_iterations += 1`，超过上限 → 转移到 RETURN_TO_CITY

- **`_step_return_to_city(scene)`** — 导航回主城。scene == main_city 时转移到 CHECK_COMPLETION。

- **`_step_check_completion(screenshot)`** — 调用 `quest_bar_detector.detect()`，检查 `has_green_check`。有对勾 → 转移到 CLAIM_REWARD。无对勾 → 回到 CLICK_QUEST 继续执行（有重试上限）。

- **`_step_claim_reward(screenshot)`** — 点击 quest 文本区域领取奖励（绿色对勾状态下点击 quest 文本即可领取），等待动画。转移到 VERIFY。

- **`_step_verify(screenshot)`** — 调用 `quest_bar_detector.detect()`，读取新的 `current_quest_text`。如果与 `target_quest_name` 不同 → quest 完成，转移到 IDLE。相同 → 可能还有奖励，重试或放弃。

### 3. `brain/llm_planner.py`

添加新方法 `analyze_quest_execution(screenshot, quest_name, game_state) -> list[dict]`：

新增 prompt `QUEST_EXECUTION_PROMPT`：
```
你是冰封岛屿游戏的AI助手。玩家正在执行任务："{quest_name}"。
分析截图，建议 1-5 个操作来推进该任务。
如果任务看起来已完成，建议返回主城的操作。
输出格式同 UNKNOWN_SCENE_PROMPT。
```

复用现有的 `_call_vision_api()` 和 `_parse_scene_response()`。

### 4. `state/game_state.py`

添加字段：
```python
# Quest bar 状态（每次主城截图更新）
self.quest_bar_visible: bool = False
self.quest_bar_has_red_badge: bool = False
self.quest_bar_current_quest: str = ""
self.quest_bar_has_green_check: bool = False
self.quest_bar_has_tutorial_finger: bool = False

# Quest workflow 执行状态（跨迭代持久化）
self.quest_workflow_phase: str = "idle"
self.quest_workflow_target: str = ""  # 正在执行的 quest 名称
```

在 `to_dict()` / `from_dict()` / `summary_for_llm()` 中添加对应序列化。

### 5. `state/state_tracker.py`

- 构造函数中创建 `QuestBarDetector(template_matcher, ocr_locator)`
- 在 `update()` 方法的 `scene == "main_city"` 分支中增加 `self._update_quest_bar(screenshot)`
- `_update_quest_bar()` 调用 `quest_bar_detector.detect()` 并将结果写入 `game_state` 字段

### 6. `brain/auto_handler.py`

- 在 `CLAIM_TEXT_PATTERNS` 中增加 `"一键领取"`

### 7. `main.py`

**`GameBot.__init__()`** 中创建并注入 `QuestWorkflow`：
```python
from brain.quest_workflow import QuestWorkflow
self.quest_workflow = QuestWorkflow(
    quest_bar_detector=self.state_tracker.quest_bar_detector,
    element_detector=self.detector,
    llm_planner=self.llm_planner,
    game_state=self.game_state,
)
```

**auto_loop 决策层**在 step 6 和 step 7 之间插入 workflow 驱动：
```python
# 6.5 Quest workflow 状态机
if self.quest_workflow.is_active():
    actions = self.quest_workflow.step(screenshot, scene)
    if actions:
        self._execute_validated_actions(actions, scene, screenshot)
        self.persistence.save(self.game_state)
        time.sleep(config.LOOP_INTERVAL)
        continue
```

**step 7 的空闲分支**中自动启动 workflow：
```python
else:
    if (scene == "main_city" and
            self.game_state.quest_bar_visible and
            self.game_state.quest_bar_current_quest):
        self.quest_workflow.start()
        continue
    actions = self.auto_handler.get_actions(screenshot, self.game_state)
```

**popup 处理（step 3）**中增加领取奖励优先：
```python
if scene == "popup":
    reward_action = self.auto_handler._check_rewards(screenshot)
    if reward_action:
        self._execute_validated_actions([reward_action], scene, screenshot)
        time.sleep(0.5)
        continue
    self.popup_filter.handle(screenshot)
    ...
```

## 安全保护

- **执行上限：** `EXECUTE_QUEST` 阶段最多 20 次迭代，超过后导航回城
- **重试上限：** `CHECK_COMPLETION` 最多 3 次重试，`VERIFY` 最多 3 次重试
- **优雅退出：** 各阶段检测到 quest bar 不可见时调用 `abort()` 回到 `IDLE`
- **模板缺失：** `tutorial_finger` 模板不存在时优雅跳过，回退到 LLM 分析

## 日志观察

运行时关注 `Quest workflow:` 前缀的日志输出：

```
Quest workflow: starting
Quest workflow: at main city, moving to READ_QUEST
Quest workflow: target quest = '升级城堡到3级'
Quest workflow: clicking quest text '升级城堡到3级' at (300, 1640)
Quest workflow: tutorial finger at (540, 960)
Quest workflow: back at main city, checking completion
Quest workflow: green check detected, claiming reward
Quest workflow: claiming reward at (300, 1640)
Quest workflow: quest changed from '升级城堡到3级' to '训练10个步兵', quest complete!
```

## 验证方式

1. `python main.py` → `scene` 确认主城识别正常
2. `python main.py` → `status` 查看 quest_bar 字段是否正确填充
3. `python main.py --auto --loops 30` 观察日志：
   - 是否成功读取 quest 名称
   - 是否点击 quest 后跳转
   - EXECUTE_QUEST 阶段是否正确调用 LLM 或跟随手指
   - 是否检测到绿色对勾
   - 是否领取奖励后 quest 名称发生切换
4. 检查卷轴红色徽标 → 优先领取奖励的流程是否正确执行

## 测试

```bash
python -m pytest test_quest_workflow.py -v
```

覆盖 35 个测试用例：QuestBarDetector 检测逻辑（8 个）+ QuestWorkflow 状态机转移（27 个，含完整生命周期端到端测试）。
