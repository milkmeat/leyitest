# SLGrobot 快速上手

## 启动方式

```bash
# 交互式 CLI（默认）
python main.py

# 自动决策循环
python main.py --auto

# 自动模式，限制循环次数
python main.py --auto --loops 50

# 指定游戏配置
python main.py --game westgame2

# 指定模拟器
python main.py --emulator ldplayer

# 单条命令模式（执行后立即退出）
python main.py <命令> [参数...]
```

## 单条命令示例

```bash
# 基础操作
python main.py tap 100,200
python main.py swipe 100,200 300,400 500
python main.py longpress 540,960 2000
python main.py screenshot test_label
python main.py center

# 状态查询
python main.py status
python main.py state
python main.py scene
python main.py dom
python main.py dom --save

# 脚本执行
python main.py scripts
python main.py run collect_resource
python main.py run collect_resource --dry
python main.py quest 派遣3名镇民
python main.py quest claim_quest_reward
python main.py quest_rules
python main.py quest_test 派遣3名镇民

# 调试工具
python main.py auto_test screenshot.png
python main.py detect_finger
python main.py detect_close_x
python main.py find_building 兵营
python main.py press_read
python main.py capture_template buttons close 450,100 630,180
python main.py reload_templates

# 游戏管理
python main.py games
python main.py game
python main.py game westgame2

# 自动循环
python main.py auto 10
```

## CLI 命令一览

### 基础操作

| 命令 | 说明 |
|------|------|
| `tap <x>,<y>` | 点击指定坐标 |
| `swipe <x1>,<y1> <x2>,<y2> [ms]` | 滑动（默认 300ms）|
| `longpress <x>,<y> [ms]` | 长按（默认 1000ms）|
| `screenshot [label]` | 截图并保存到 `data/screenshots/` |
| `center` | 点击屏幕中心 |

### 状态查询

| 命令 | 说明 |
|------|------|
| `status` | 显示连接状态和游戏状态概览 |
| `state` | 显示当前游戏状态（LLM 摘要格式）|
| `scene` | 检测当前场景（通过 Screen DOM）|
| `dom [--save]` | 构建当前屏幕的 YAML DOM（含所有交互元素）|

### 脚本执行

| 命令 | 说明 |
|------|------|
| `scripts` | 列出所有可用的 YAML 脚本 |
| `run <name> [--dry]` | 执行 YAML 脚本（v2 DOM-aware runner）|
| `quest <name or text>` | 执行任务脚本（支持脚本名称或文本匹配）|
| `quest_rules` | 列出所有任务脚本规则（名称 + 正则模式）|
| `quest_test <name or text>` | 干运行任务脚本（仅显示步骤）|

### 调试工具

| 命令 | 说明 |
|------|------|
| `auto_test <png_file>` | 在截图上模拟一次自动循环（干运行）|
| `detect_finger` | 检测教程手指，打印坐标，保存裁剪图 |
| `detect_close_x` | 检测 close_x 按钮，打印坐标，保存裁剪图 |
| `find_building <name>` | 在城市地图上查找建筑并点击 |
| `press_read` | 按压拖动读取：显示所有可见的建筑名称 |
| `capture_template <category> <name> <x1>,<y1> <x2>,<y2>` | 截取屏幕区域作为模板 |
| `reload_templates` | 重新加载模板库 |

### 游戏管理

| 命令 | 说明 |
|------|------|
| `games` | 列出所有可用的游戏配置 |
| `game [id]` | 显示当前游戏（或指定游戏 ID 的信息）|

### 自动循环

| 命令 | 说明 |
|------|------|
| `auto [loops]` | 启动自动循环（不传参数则无限循环，Ctrl+C 停止）|

### 其他

| 命令 | 说明 |
|------|------|
| `help` | 显示帮助 |
| `exit` / `quit` | 退出 |

## Quest 脚本系统

### 使用方式

Quest 脚本现在支持两种匹配方式：**按名称**（精确匹配）和**按正则模式**（模糊匹配）。

```bash
# 查看所有已定义的任务脚本
> quest_rules
5 quest script(s):
  1. collect_resource  /收集.*资源/  (3 steps)
      收集资源
      1. tap: territory (点击领地按钮)
      2. wait: 1.0s (等待)
      3. tap: down_triangle (点击下拉三角)

  2. claim_quest_reward  /领取任务奖励/  (2 steps)
      领取任务栏奖励
      1. tap: green_check (点击绿色勾选)
      2. wait: 0.5s (等待)

# 按名称执行（精确匹配）
> quest claim_quest_reward
Matched rule: claim_quest_reward  (2 steps)
  Step 1/2: tap green_check — 领取任务栏奖励
  Step 2/2: wait 0.5s — 等待
Quest script completed (2 steps)

# 按文本执行（正则匹配）
> quest 派遣3名镇民
Matched rule: dispatch_citizens  /派遣.*镇民/  (2 steps)
  Step 1/2: tap [790, 1815] — 切换到镇民标签
  Step 2/2: tap [750, 1598] — 点击+添加镇民
Quest script completed (2 steps)

# 干运行（不实际执行，仅显示步骤）
> quest_test 派遣3名镇民
Matched: dispatch_citizens  /派遣.*镇民/  (2 steps)
Dry run for quest text: '派遣3名镇民'
  1. [tap] (790, 1815)  delay=1.0s
      切换到镇民标签
  2. [tap] (750, 1598)  delay=1.5s
      点击+添加镇民
```

### 添加新规则

在 `games/<game_id>/scripts/` 目录下创建 YAML 文件，详细语法参见 `quest_scripting.md`。

示例脚本文件 `games/westgame2/scripts/collect_resource.yaml`：

```yaml
name: collect_resource
pattern: "收集.*资源"
description: 收集资源
steps:
  - action: tap
    target: territory
    description: 点击领地按钮
  - action: wait
    duration: 1.0
    description: 等待
  - action: tap
    target: down_triangle
    description: 点击下拉三角
```

### 自动触发

自动循环中，当任务栏文本匹配到规则的 `pattern` 时，脚本会自动执行。
无需手动输入 `quest` 命令。

## 自动循环流程

```
截图 → 构建 DOM（含场景推断）→
  特殊场景预检查 →
    tutorial_finger → 跟随点击 → 下一轮
    exit_dialog → 点击"继续" → 冷却 60 秒 → 下一轮
    shoot_mini_game → 滑动射击 → 下一轮
  主城场景 → 更新游戏状态（资源、建筑、任务栏）
  优先级规则（auto_handler）→
    popup → 自动关闭 → 下一轮
    loading → 等待 → 下一轮
    quest_bar 有绿色勾 → 领取奖励 → 下一轮
    quest_bar 有任务且匹配脚本 → 执行任务脚本 → 下一轮
    其他 → AutoHandler 自动操作 → 下一轮
  卡住检测 → 恢复操作 → 下一轮
  → 持久化状态 → 等待 → 下一轮
```

### 错误恢复

- ADB 断开连接时自动重连
- 连续截图失败时尝试重连
- 场景卡住时进行恢复操作（点击空白区域、返回等）
- 连续错误超过 5 次时停止循环

## 游戏状态

游戏状态自动持久化到 `games/<game_id>/game_state.json`，包含：

- 当前场景（main_city / world_map / battle / popup / loading 等）
- 资源数量（根据游戏配置，如 food / wood / stone / gold）
- 建筑信息（名称、等级、是否升级中）
- 任务栏信息（当前任务、是否有绿色勾、是否有红点）
- 行军状态
- 操作历史

重启后自动恢复，不丢失数据。
