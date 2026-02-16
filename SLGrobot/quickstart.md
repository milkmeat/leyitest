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
python main.py task collect_resources 5
python main.py tasks
python main.py save_tasks
python main.py load_tasks
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
| `task <name> [priority]` | 添加任务到队列 |
| `tasks` | 查看任务队列 |
| `save_tasks` | 保存任务队列到 `data/tasks.json` |
| `load_tasks` | 从 `data/tasks.json` 恢复任务队列 |
| `auto [loops]` | 启动自动循环（不传参数则无限循环，Ctrl+C 停止）|
| `help` | 显示帮助 |
| `exit` / `quit` | 退出 |

## 任务系统

### 支持的任务

| 任务名 | 说明 | 参数 |
|--------|------|------|
| `collect_resources` | 收集生产资源 | — |
| `upgrade_building` | 升级建筑 | `building_name`: 建筑名 |
| `train_troops` | 训练兵种 | — |
| `claim_rewards` | 领取奖励 | — |
| `navigate_main_city` | 回到主城 | — |
| `navigate_world_map` | 去世界地图 | — |
| `close_popup` | 关闭弹窗 | — |
| `check_mail` | 查看邮件 | — |
| `collect_daily` | 领取每日奖励 | — |

### 任务工作流

```bash
# 1. 添加任务（数字是优先级，越大越优先）
> task upgrade_building 10
> task collect_resources 5
> task check_mail 1

# 2. 查看队列
> tasks
  [pending] upgrade_building (priority=10, retries=0)
  [pending] collect_resources (priority=5, retries=0)
  [pending] check_mail (priority=1, retries=0)

# 3. 保存到文件（可手动编辑）
> save_tasks

# 4. 启动自动循环执行
> auto 20
```

### 任务持久化

任务保存为可读的 JSON 文件 `data/tasks.json`：

```json
[
  {
    "name": "upgrade_building",
    "priority": 10,
    "params": {},
    "status": "pending",
    "retry_count": 0,
    "max_retries": 3
  }
]
```

可以直接编辑这个文件来预配置任务，然后用 `load_tasks` 加载。

### 任务执行逻辑

- 自动循环按优先级从高到低取任务
- 任务由 `RuleEngine` 分解为具体动作（OCR 定位按钮 → 点击）
- 执行失败自动重试，最多 3 次
- 队列为空时，`AutoHandler` 接管：自动关闭弹窗、领取奖励、跳过加载

## 自动循环流程

```
截图 → 场景分类 →
  popup  → 自动关闭 → 下一轮
  loading → 等待 → 下一轮
  其他场景 → 更新游戏状态 →
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
