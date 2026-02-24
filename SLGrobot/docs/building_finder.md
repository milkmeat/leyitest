# Building Finder - 城市地图建筑查找与点击

## 概述

BuildingFinder 在可滚动的城市地图上查找并点击指定建筑。城市地图大于屏幕可视区域，需要滚动才能看到所有建筑。建筑名称只在玩家按下并拖动屏幕时显示，松手后消失。

## 核心原理：Press-Drag-Read

### 游戏机制

1. 按下屏幕任意位置
2. 拖动至少 60px（不松手）
3. 建筑名称立即显示在所有可见建筑上方
4. 只要不松手，名称保持可见
5. 松手后名称消失

### ADB 实现

使用 `adb shell input swipe` 模拟拖动手势：

```
adb shell input swipe 540 960 690 1110 3000
```

- 起点：(540, 960) — 屏幕中心
- 终点：(690, 1110) — 偏移 150px（对角线方向）
- 持续时间：3000ms — 线性插值，约 1200ms 时越过 60px 阈值

### 线程模型

`adb input swipe` 会阻塞直到手势完成。为了在手指按住期间截图，使用后台线程运行 swipe，主线程在延迟后截图：

```
t=0ms       swipe 命令开始（手指按下）
t=1200ms    手指移动 60px，建筑名称出现
t=1400ms    主线程截图（名称可见） ← screenshot_delay_ms
t=1400-2000 OCR 处理
t=3000ms    swipe 结束（手指抬起，名称消失）
t=3300ms    在记录的位置点击建筑
```

### 漂移补偿

截图时 swipe 只走了一部分（约 70px），之后继续移动至 150px。地图跟随手指移动，所以截图中记录的建筑位置与松手后的实际位置有偏差。

补偿公式：
```
remaining_ratio = 1.0 - (screenshot_delay_ms / hold_duration_ms)
drift = drag_offset * remaining_ratio
tap_position = bbox_top_left + tap_offset + (drift, drift)
```

当前参数：`1.0 - 1400/3000 = 0.533`，`drift = 150 * 0.533 ≈ 80px`

### 点击位置计算

OCR 返回的 bbox 左上角坐标 + 配置偏移量 + 漂移补偿 = 最终点击位置：

```
tap_x = bbox.x1 + tap_offset_x + drift
tap_y = bbox.y1 + tap_offset_y + drift
```

## 架构

```
QuestScript / RuleEngine / CLI
         │
         ▼
   ┌─────────────────┐
   │  BuildingFinder  │  vision/building_finder.py
   │                  │
   │  find_and_tap()  │  主入口（迭代式导航）
   │    ├─ _press_drag_read_full() 按住拖动、OCR、返回全部结果+目标位置
   │    ├─ _estimate_position()    通过可见建筑估算视口位置
   │    └─ _scroll_by()            执行滚动（分步+限幅）
   └─────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
  ADB       OCR
(swipe,    (screenshot,
 tap)      find_all_text)
```

## 文件

| 文件 | 作用 |
|------|------|
| `vision/building_finder.py` | BuildingFinder 类 + MD 布局表解析器 |
| `games/<id>/city_layout.md` | 建筑布局数据（用户填写） |
| `games/<id>/game.json` → `city_layout` | 配置参数 |

## 配置参数

在 `game.json` 的 `city_layout` 字段中配置：

```json
{
  "city_layout": {
    "file": "city_layout.md",
    "reference_building": "城镇中心",
    "pixels_per_unit": 400,
    "hold_point": [540, 960],
    "hold_duration_ms": 3000,
    "screenshot_delay_ms": 1400,
    "drag_offset": 150,
    "tap_offset_x": 100,
    "tap_offset_y": 150
  }
}
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `file` | 布局文件路径（相对游戏目录） | `city_layout.md` |
| `reference_building` | 参考建筑名（布局原点） | `城堡` |
| `pixels_per_unit` | 布局表中每格对应的像素 | 400 |
| `hold_point` | 按下位置（屏幕坐标） | [540, 960] |
| `hold_duration_ms` | swipe 总持续时间 | 3000 |
| `screenshot_delay_ms` | 截图延迟（需 > 60px 到达时间） | 1400 |
| `drag_offset` | swipe 总偏移量（像素） | 150 |
| `tap_offset_x` | bbox 左上角到建筑中心的 x 偏移 | 100 |
| `tap_offset_y` | bbox 左上角到建筑中心的 y 偏移 | 150 |
| `safe_zone` | [x1, y1, x2, y2] 有效建筑区域 | [100, 200, 900, 1500] |

### Safe Zone

屏幕上除了地图建筑名称外，还有 UI 元素（如 quest bar）也包含建筑名称文字。例如任务栏显示"将5号起居室升至6级"，OCR 会识别出"5号起居室"。如果不过滤，`_estimate_position` 会把 quest bar 上的文字当作地图上的建筑来估算视口位置，导致导航偏移无法收敛。

`safe_zone` 定义了地图建筑名称可能出现的屏幕区域 `[x1, y1, x2, y2]`。OCR 结果中心点不在此区域内的文字会被忽略，不参与目标匹配和位置估算。

### 参数调校要点

- `drag_offset / hold_duration_ms` 决定了 60px 何时被越过。当前 150px/3000ms → 60px 在 ~1200ms
- `screenshot_delay_ms` 必须大于 60px 到达时间，且小于 `hold_duration_ms`
- `tap_offset_x/y` 根据建筑名称标签相对建筑中心的位置调整

## 城市布局文件格式

`city_layout.md` 使用 Markdown 表格，建筑放在棋盘格的交替单元格上（类似黑格），直接对应等距游戏视角：

```markdown
|   | 1 |   | 3 |   | 5 |   | 7 |
|---|---|---|---|---|---|---|---|
|   |   | 农场 |   |   |   | 伐木场 |   |
| 2 |   |   | 采石场 |   | 铁矿 |   |   |
|   |   |   |   | 城镇中心 |   |   |   |
| 4 |   |   | 仓库 |   | 兵营 |   |   |
```

解析器：
1. 读取表格行，按 `|` 分割
2. 非空单元格 = 建筑，跳过纯数字的行/列标题
3. 找到参考建筑位置作为原点 (0,0)
4. 计算所有建筑相对于参考建筑的像素偏移

## 导航策略：迭代式位置修正

每次 press-drag-read 都会轻微移动地图，因此不能用一次性估算+滚动。采用迭代方式：

1. **press-drag-read**：同时获取目标位置（如在屏幕上）和所有可见建筑
2. **如果找到目标**：直接点击，完成
3. **如果未找到**：用可见建筑估算当前视口中心，计算到目标的偏移，滚动
4. **重复步骤 1-3**：每次滚动后重新估算位置，逐步逼近目标
5. **终止条件**：找到目标 / 估算偏移很小但看不到目标 / 达到最大尝试次数

## Quest Script 集成

### 新动词：`find_building`

```json
{"find_building": ["兵营"], "delay": 2.0, "description": "找到并点击兵营"}
{"find_building": ["兵营", {"scroll": true, "max_attempts": 5}], "delay": 2.0}
```

### Action Dict

```python
{"type": "find_building", "building_name": "兵营", "scroll": True, "max_attempts": 3}
```

由 `executor/action_runner.py` 的 `_execute_find_building()` 处理。

### 使用示例

```json
{
  "pattern": "将兵营升至\\d+级",
  "steps": [
    {"ensure_main_city": [], "delay": 1.5, "description": "回到主城"},
    {"find_building": ["兵营"], "delay": 2.0, "description": "找到并点击兵营"},
    {"tap_text": ["升级"], "delay": 1.5, "description": "点击升级"},
    {"tap_text": ["确定"], "delay": 1.5, "optional": true, "description": "确认"}
  ]
}
```

## CLI 命令

### `find_building <name>`

在城市地图上查找并点击指定建筑。

```bash
python main.py find_building 城镇中心
python main.py find_building 5号起居室
```

### `press_read`

调试/校准命令。执行一次 press-drag-read，显示屏幕上所有 OCR 检测到的文本及坐标。

```bash
python main.py press_read
```

输出示例：
```
Detected 34 building(s):
  城镇中心                  (547, 938)
  1号起居室                 (899, 1389)
  木材厂                   (70, 514)
  ...
```

## 错误处理

| 场景 | 处理 |
|------|------|
| 截图失败 | 捕获异常，join 线程，返回 None，调用方重试 |
| OCR 无结果 | 可能 hold_point 在 UI 元素上，或时序不对 |
| 目标未在 OCR 结果中 | 尝试滚动+重试。超过 max_attempts 返回 False |
| 线程挂起 | `thread.join(timeout=5)`，daemon 线程随进程退出 |
| 布局中无匹配建筑 | 无法估算位置，返回 False |
| 并发 ADB 失败 | 已在 Nox 上验证可行 |
