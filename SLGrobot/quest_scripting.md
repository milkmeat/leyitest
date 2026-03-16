# Quest Scripting — YAML Script Reference

## 概述

Quest Scripting 系统将游戏操作定义为 YAML 脚本，存放在 `games/<id>/scripts/` 目录下。每个脚本有一个 `name`（英文标识）和可选的 `pattern`（中文正则，用于自动匹配任务栏文字）。

CLI 支持双语匹配：`quest claim_quest_reward` 或 `quest 领取任务奖励` 均可。

---

## 架构

### 核心组件

| 文件 | 角色 |
|------|------|
| `brain/script_runner.py` | `ScriptRunner` — 统一脚本执行引擎 |
| `games/<id>/scripts/*.yaml` | 脚本定义（YAML） |
| `main.py` | `cmd_quest` / `cmd_quest_rules` / `cmd_quest_test` — CLI 命令 |

### 执行流程

```
CLI: quest 领取任务奖励
  → _match_quest_rule() 正则匹配
  → ScriptRunner.run(script)
    → 逐步执行 steps[]
    → 每步按 action 类型分发到 handler
    → handler 内部调用 ADB/OCR/TemplateMatcher
```

---

## YAML 脚本格式

```yaml
name: claim_quest_reward          # 英文标识（CLI 精确匹配）
pattern: "领取任务奖励"             # 正则模式（CLI 和自动循环匹配）
description: "领取所有任务奖励"     # 可选描述
steps:
  - action: ensure_main_city
    max_retries: 10
    wait: 1.5

  - action: tap
    pos: [70, 1600]               # 固定坐标
    wait: 2.0

  - action: tap
    target: {type: text, value: "领取", nth: -1}
    region: [0, 1350, 1080, 1500] # 可选：OCR 区域限制
    wait: 1.5
    repeat: 10                     # 重复执行次数
    optional: true                 # 目标未找到时跳过（而非中止）
```

---

## Action 类型

### tap
点击屏幕位置或目标元素。

```yaml
- action: tap
  pos: [x, y]                     # 固定坐标（与 target 二选一）
  target: {type: text, value: "升级"}  # 目标查找（与 pos 二选一）
  region: [x1, y1, x2, y2]        # 可选：OCR 限制区域
  offset_x: 0                     # 可选：点击 X 偏移
  offset_y: 10                    # 可选：点击 Y 偏移
  wait: 1.5                       # 点击后等待秒数
  repeat: 3                       # 重复次数（默认 1）
  optional: true                  # 目标未找到时跳过（默认 false）
```

### swipe
滑动手势。

```yaml
- action: swipe
  from: [640, 500]
  to: [640, 200]
  duration_ms: 300
  wait: 0.5
```

### wait
等待指定秒数。

```yaml
- action: wait
  seconds: 2
```

### wait_for
轮询等待目标出现。

```yaml
- action: wait_for
  target: {type: text, value: "升级完成"}
  timeout: 60                      # 超时秒数（默认 30）
  poll_interval: 2                 # 轮询间隔（默认 2）
```

### ensure_main_city / ensure_world_map
导航到主城或世界地图，带重试逻辑。

```yaml
- action: ensure_main_city
  max_retries: 10                  # 最大重试次数（默认 10）
  wait: 1.5
```

导航策略：检测当前场景 → 如果在目标场景则完成 → 否则尝试 back_arrow → close_x → 空白区域点击 → 超过次数则中止。

### find_building
在城市地图上查找并点击建筑。

```yaml
- action: find_building
  building: "{building}"           # 建筑名（支持变量替换）
  scroll: true                     # 是否滚动查找
  max_attempts: 3
  wait: 2.0
```

### read_text
OCR 读取区域文字并存入变量。

```yaml
- action: read_text
  region: [400, 900, 600, 960]     # [x1, y1, x2, y2]
  var: "level"                     # 存入的变量名
```

### eval
对变量进行安全算术运算。

```yaml
- action: eval
  var: "next_level"
  expr: "{level} + 1"              # 支持 +, -, *, //, %
```

### if
条件分支执行。

```yaml
- action: if
  condition:
    exists: {type: text, value: "资源不足"}
  then:
    - action: tap
      pos: [680, 1000]
  else:
    - action: tap
      pos: [400, 1000]
```

条件支持：`exists`, `not_exists`, `scene`, `all`, `any`。

---

## Target 类型与内部实现

| target.type | 内部实现 | 是否构建 DOM | 支持 nth | 支持 region |
|---|---|---|---|---|
| `text` | OCRLocator.find_all_text() | ❌ | ✅ | ✅ |
| `icon` | TemplateMatcher.match_one_multi() | ❌ | ✅ | ❌ |
| `primary_button` | element_detector.find_primary_button() | ❌ | ❌ | ❌ |
| `button` | ScreenDOMBuilder.build() → find_element() | ✅ | ✅ | ❌ |
| `red_dot` / `green_check` / `finger` | DOM 查找 | ✅ | ✅ | ❌ |

**性能优化**：`text` 和 `icon` 类型不构建 DOM，直接调用底层组件，适合 `repeat: 10` 场景。

---

## 变量系统

- 变量用 `{var_name}` 语法引用
- `read_text` 写入变量，`eval` 计算表达式
- 正则 pattern 中的命名组 `(?P<name>...)` 自动注入变量
- 示例：`pattern: "采集(?P<resource_type>小麦|木材)"` → `{resource_type}` 可用

---

## CLI 命令

```bash
quest <name or text>       # 执行匹配的脚本
quest_rules                # 列出所有脚本
quest_test <name or text>  # 预览步骤（dry run）
run <name> [--dry]         # 按文件名执行 YAML 脚本
scripts                    # 列出 scripts/ 目录中所有脚本
```

---

## 脚本文件位置

```
games/westgame2/scripts/
├── claim_expedition_reward.yaml
├── claim_quest_reward.yaml
├── collect_resource.yaml
├── dispatch_citizens.yaml
├── pass_expedition.yaml
├── train.yaml
└── upgrade_building.yaml
```
