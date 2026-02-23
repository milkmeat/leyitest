# SLGrobot 快速上手

## 启动方式

```bash
# 交互式 CLI（默认）
python main.py

# 自动决策循环
python main.py --auto

# 自动模式，限制循环次数
python main.py --auto --loops 50

# 单条命令模式（执行后立即退出）
python main.py <命令> [参数...]
```

## 单条命令示例

```bash
python main.py tap 100,200
python main.py swipe 100,200 300,400 500
python main.py longpress 540,960 2000
python main.py screenshot test_label
python main.py back
python main.py home
python main.py center
python main.py status
python main.py state
python main.py scene
python main.py quest 派遣3名镇民
python main.py quest_rules
python main.py quest_test 派遣3名镇民
python main.py auto 10
```

## CLI 命令一览

| 命令 | 说明 |
|------|------|
| `tap <x>,<y>` | 点击指定坐标 |
| `swipe <x1>,<y1> <x2>,<y2> [ms]` | 滑动（默认 300ms）|
| `longpress <x>,<y> [ms]` | 长按（默认 1000ms）|
| `screenshot [label]` | 截图并保存到 `data/screenshots/` |
| `back` | 按 Android 返回键 |
| `home` | 按 Android Home 键 |
| `center` | 点击屏幕中心 |
| `status` | 显示连接状态和游戏状态概览 |
| `state` | 显示当前游戏状态（LLM 摘要格式）|
| `scene` | 截图并分类当前场景（含置信度）|
| `quest <quest text>` | 执行匹配的任务脚本 |
| `quest_rules` | 列出所有任务脚本规则 |
| `quest_test <quest text>` | 干运行任务脚本（仅显示步骤）|
| `auto [loops]` | 启动自动循环（不传参数则无限循环，Ctrl+C 停止）|
| `llm` | 手动触发 LLM 战略咨询 |
| `help` | 显示帮助 |
| `exit` / `quit` | 退出 |

## Quest 脚本系统

### 使用方式

```bash
# 查看所有已定义的任务脚本
> quest_rules
1 quest action rule(s):
  1. /派遣.*镇民/  (2 steps)
      1. tap_xy=[790, 1815]  切换到镇民标签
      2. tap_xy=[750, 1598] x3  点击+添加镇民

# 干运行（不实际执行，仅显示步骤）
> quest_test 派遣3名镇民
Matched: /派遣.*镇民/  (2 steps)
Dry run for quest text: '派遣3名镇民'
  1. [tap_xy] (790, 1815)  delay=1.0s
     切换到镇民标签
  2. [tap_xy] (750, 1598)  delay=1.5s x3
     点击+添加镇民

# 实际执行
> quest 派遣3名镇民
Matched rule: '派遣.*镇民' (2 steps)
  Step 1/2: tap (790, 1815) — quest_script:tap_xy:790,1815:切换到镇民标签
  Step 2/2: tap (750, 1598) — quest_script:tap_xy:750,1598:点击+添加镇民
  ...
Quest script completed (2 steps)
```

### 添加新规则

在 `games/<game_id>/game.json` 的 `quest_action_rules` 中添加规则，
详细语法参见 `quest_scripting.md`。

### 自动触发

自动循环中，当任务栏文本匹配到规则的 `pattern` 时，脚本会自动执行。
无需手动输入 `quest` 命令。

## 自动循环流程

```
截图 → 场景分类 →
  popup  → 自动关闭 → 下一轮
  loading → 等待 → 下一轮
  tutorial_finger → 跟随点击 → 下一轮
  quest workflow 活跃 → 执行任务脚本 → 下一轮
  其他场景 → 更新游戏状态 →
    主城有 quest 栏 → 启动 Quest Workflow
    有待处理任务 → RuleEngine 分解执行
    无任务 → AutoHandler 自动操作
  → 持久化状态 → 等待 2 秒 → 下一轮
```

## 游戏状态

游戏状态自动持久化到 `data/game_state.json`，包含：

- 当前场景（main_city / world_map / battle / popup / loading）
- 资源数量（food / wood / stone / gold）
- 建筑信息（名称、等级、是否升级中）
- 行军状态
- 操作历史

重启后自动恢复，不丢失数据。
