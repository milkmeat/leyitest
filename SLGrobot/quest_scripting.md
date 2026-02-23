# Quest Scripting Language & Unified Execution System

## 概述

Quest Scripting 系统将游戏操作定义为 JSON 脚本，通过模式匹配自动执行。用户可以从 CLI 输入任务文本（如同从任务栏读取），也可以在自动循环中任务栏显示匹配文本时自动触发。

此系统替代了原有的 `task` + `RuleEngine` 单步操作模式，提供确定性多步骤执行序列。

---

## 架构

### 核心组件

| 文件 | 角色 |
|------|------|
| `brain/quest_script.py` | `QuestScriptRunner` — 脚本执行引擎 |
| `brain/quest_workflow.py` | `QuestWorkflow._match_quest_rule()` — 自动循环中的脚本调度 |
| `games/<id>/game.json` | `quest_action_rules` — 脚本定义（JSON） |
| `main.py` | `cmd_quest` / `cmd_quest_rules` / `cmd_quest_test` — CLI 命令 |

### 执行流程

```
CLI "quest 派遣3名镇民"
  → 正则匹配 "派遣.*镇民"
  → QuestScriptRunner.load(steps)
  → 循环:
      screenshot → execute_one() → action dict → ActionRunner.execute() → 输出进度
  → 完成

自动循环（任务栏显示 "派遣3名镇民"）
  → QuestWorkflow._match_quest_rule()
  → QuestScriptRunner.execute_one() 每次迭代执行一步
  → 返回 action dicts 给现有执行管线
```

### 与现有系统的关系

```
auto_loop 决策层（优先级从高到低）：
  popup/loading         → 现有处理
  tutorial_finger       → 跟随手指点击
  Workflow 活跃         → workflow.step() → _match_quest_rule() → QuestScriptRunner
  TaskQueue 有任务      → rule_engine.plan()（保留作为兜底）
  LLM 咨询              → llm_planner 生成任务
  空闲 + 主城有 quest 栏 → 启动 Workflow
  空闲                  → auto_handler
```

---

## QuestScriptRunner API

```python
class QuestScriptRunner:
    def __init__(self, ocr_locator, template_matcher, adb_controller, screenshot_fn=None)
    def load(self, steps: list[dict]) -> None       # 加载脚本，重置状态
    def reset(self) -> None                          # 重置执行位置，不清除脚本
    def is_done(self) -> bool                        # 所有步骤是否执行完毕
    def execute_one(self, screenshot) -> list[dict] | None
        # 返回 action dicts: 成功执行
        # 返回 []: 无操作步骤（read_text, eval）
        # 返回 None: 等待条件满足（如文本未找到）
```

### 变量系统

Runner 内维护 `self.variables: dict[str, str]`，`read_text` 写入、`eval` 计算、可在后续步骤中引用。

---

## 脚本动词参考

### `tap_xy` — 坐标点击

```json
{"tap_xy": [x, y], "delay": 1.0, "description": "说明"}
```

无条件点击固定坐标。始终成功。

### `tap_text` — OCR 文本点击

```json
{"tap_text": ["目标文本"], "delay": 1.0, "description": "点击第一个匹配"}
{"tap_text": ["目标文本", 2], "delay": 1.0, "description": "点击第2个匹配"}
```

OCR 搜索屏幕上的文本，点击第 nth 个匹配（1-indexed，默认 1）。
文本未找到时返回 `None`，下次迭代重试。

### `tap_icon` — 模板图标点击

```json
{"tap_icon": ["buttons/upgrade"], "delay": 1.0, "description": "点击升级按钮"}
{"tap_icon": ["icons/food", 2], "delay": 1.0, "description": "点击第2个食物图标"}
```

使用 `TemplateMatcher.match_one_multi()` 查找所有匹配，点击第 nth 个（1-indexed）。
图标未找到时返回 `None`，下次迭代重试。

### `wait_text` — 等待文本出现

```json
{"wait_text": ["目标文本"], "description": "等待文本出现在屏幕上"}
```

OCR 搜索屏幕上的文本，找到后推进到下一步。不产生点击动作。
文本未找到时返回 `None`，下次迭代重试。

适用场景：等待战斗结束、等待加载完成等需要确认屏幕状态再继续的步骤。

### `read_text` — 区域 OCR 读取

```json
{"read_text": [x, y, "var_name"], "description": "默认 200x80 区域"}
{"read_text": [x, y, "var_name", 300, 100], "description": "自定义区域大小"}
```

以 (x, y) 为中心裁剪区域（默认 200x80），OCR 识别所有文本并拼接，存入 `self.variables[var_name]`。
不产生点击动作。

### `eval` — 表达式计算

```json
{"eval": ["result", "{level} + 1"], "description": "计算表达式"}
```

安全表达式求值器。变量以 `{var_name}` 引用。支持算术运算和 `int()`、`str()`、`len()`、`abs()`。
使用 `ast` 模块安全解析，禁止 `exec`/`import`/`__builtins__`。

### 通用步骤字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `delay` | float | 1.0 | 动作执行后等待秒数 |
| `repeat` | int | 1 | 重复执行此步骤 N 次 |
| `description` | str | "" | 可读描述（日志输出用） |

### 重复逻辑

每个步骤可设 `"repeat": N`。首次遇到时设 `_repeat_remaining = N`，每次成功执行递减。
`step_index` 仅在 `_repeat_remaining` 归零后前进。
`tap_text`/`tap_icon` 返回 `None`（未找到）时不递减计数器。

---

## 脚本格式示例

### 完整规则定义（game.json 中的 `quest_action_rules`）

```json
{
  "quest_action_rules": [
    {
      "pattern": "派遣.*镇民",
      "steps": [
        {"tap_xy": [790, 1815], "delay": 1.0, "description": "切换到镇民标签"},
        {"tap_xy": [750, 1598], "delay": 1.5, "repeat": 3, "description": "点击+添加镇民"}
      ]
    },
    {
      "pattern": "将.*升至\\d+级",
      "steps": [
        {"tap_text": ["升级"], "delay": 1.5, "description": "点击升级按钮"},
        {"tap_xy": [540, 1400], "delay": 1.0, "description": "确认"}
      ]
    },
    {
      "pattern": "采集.*资源",
      "steps": [
        {"tap_icon": ["icons/food"], "delay": 1.0, "description": "点击食物图标"},
        {"tap_text": ["采集"], "delay": 1.5, "description": "点击采集按钮"},
        {"read_text": [540, 800, "amount", 200, 60], "description": "读取采集量"},
        {"eval": ["total", "{amount} + 100"], "description": "计算总量"}
      ]
    }
  ]
}
```

### 使用 repeat 简化重复步骤

旧写法（3 个相同步骤）：
```json
{"tap_xy": [750, 1598], "delay": 1.5, "description": "点击+添加镇民1"},
{"tap_xy": [750, 1598], "delay": 1.5, "description": "点击+添加镇民2"},
{"tap_xy": [750, 1598], "delay": 1.5, "description": "点击+添加镇民3"}
```

新写法（1 个步骤 repeat 3 次）：
```json
{"tap_xy": [750, 1598], "delay": 1.5, "repeat": 3, "description": "点击+添加镇民"}
```

---

## CLI 命令

### `quest <quest text>` — 执行任务脚本

```bash
python main.py quest 派遣3名镇民
python main.py quest 将驻防站升至2级
```

匹配 `quest_action_rules` 中的 pattern，创建独立的 `QuestScriptRunner`，
循环执行直到完成或达到最大迭代次数。每步输出进度。

交互模式下：
```
> quest 派遣3名镇民
Matched rule: '派遣.*镇民' (2 steps)
  Step 1/2: tap (790, 1815) — quest_script:tap_xy:790,1815:切换到镇民标签
  Step 2/2: tap (750, 1598) — quest_script:tap_xy:750,1598:点击+添加镇民
  Step 2/2: tap (750, 1598) — quest_script:tap_xy:750,1598:点击+添加镇民
  Step 2/2: tap (750, 1598) — quest_script:tap_xy:750,1598:点击+添加镇民
Quest script completed (2 steps)
```

### `quest_rules` — 列出所有任务规则

```
> quest_rules
1 quest action rule(s):
  1. /派遣.*镇民/  (2 steps)
      1. tap_xy=[790, 1815]  切换到镇民标签
      2. tap_xy=[750, 1598] x3  点击+添加镇民
```

### `quest_test <quest text>` — 干运行

```
> quest_test 派遣3名镇民
Matched: /派遣.*镇民/  (2 steps)
Dry run for quest text: '派遣3名镇民'

  1. [tap_xy] (790, 1815)  delay=1.0s
     切换到镇民标签
  2. [tap_xy] (750, 1598)  delay=1.5s x3
     点击+添加镇民
```

---

## 向后兼容性

### 现有规则格式

旧格式的 `tap_text` + `tap_xy` 步骤（如 `games/westgame2/game.json` 中已有的规则）
完全兼容新引擎。`QuestScriptRunner` 支持所有旧字段：
- `tap_xy: [x, y]` — 与旧格式相同
- `tap_text: "文本"` 或 `tap_text: ["文本"]` — 均支持

### RuleEngine / TaskQueue

`brain/rule_engine.py` 和 `brain/task_queue.py` 保留不删除，自动循环中仍作为兜底。
Quest Script 覆盖所有需要的操作后可移除。

---

## 文件变更清单

| 文件 | 变更 |
|------|------|
| `brain/quest_script.py` | **新建** — QuestScriptRunner + _safe_eval |
| `brain/quest_workflow.py` | 修改 — `_match_quest_rule()` 委托给 QuestScriptRunner；`__init__` 新增 `adb_controller`/`screenshot_fn` 参数 |
| `main.py` | 修改 — 删除 `cmd_task`/`cmd_tasks`/`cmd_save_tasks`/`cmd_load_tasks`；新增 `cmd_quest`/`cmd_quest_rules`/`cmd_quest_test`；更新 help 文本 |

---

## 添加新任务脚本

1. 打开 `games/<game_id>/game.json`
2. 在 `quest_action_rules` 数组中添加新规则
3. `pattern` 为正则表达式，匹配任务栏文本
4. `steps` 为步骤数组，使用上述动词
5. 用 `quest_test` 验证匹配，用 `quest` 实际执行

建议工作流：
```bash
# 1. 查看当前任务栏文本
python main.py status

# 2. 添加规则到 game.json

# 3. 干运行验证
python main.py quest_test 派遣3名镇民到采石场

# 4. 实际执行
python main.py quest 派遣3名镇民到采石场
```
