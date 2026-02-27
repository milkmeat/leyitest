# Press-Drag-Read 实现详解

## 问题背景

SLG 城建地图上，建筑名称不是常驻显示的。玩家需要按住屏幕并拖动超过 ~60px，名称才会浮现在所有可见建筑上方；松手后名称立即消失。

这意味着机器人必须在"手指按住"的过程中完成截图和 OCR 识别。

## 核心挑战

`adb shell input swipe` 是阻塞调用——在手势完成前不会返回。因此不能在同一线程里先 swipe 再 screenshot。

**解决思路**：用 Python 多线程——后台线程执行 swipe（模拟手指按住），主线程在合适的时机截图。

## 时间轴

```
t=0ms       后台线程启动 adb swipe (540,960) → (690,1110), 持续 3000ms
t=1200ms    手指已移动 ~60px，建筑名称开始显示
t=1400ms    主线程截图（screenshot_delay_ms=1400）← 此时名称已可见
t=1400+     主线程做 OCR 识别
t=3000ms    swipe 结束，手指抬起，名称消失
t=3300ms    在补偿后的位置执行 tap
```

## 核心代码结构

位于 `vision/building_finder.py` 的 `_press_drag_read_full` 方法（第 261-355 行）：

```python
# 1. 后台线程执行 swipe（手指按住不放）
thread = threading.Thread(
    target=self.adb.swipe,
    args=(hx, hy, hx + dx, hy + dx, self.hold_duration_ms),
    daemon=True,
)
thread.start()

# 2. 主线程等待名称渲染
time.sleep(self.screenshot_delay_ms / 1000.0)   # 1.4 秒

# 3. 趁手指还按着，截图
screenshot = self.adb.screenshot()

# 4. OCR 识别所有文字
all_text = self.ocr.find_all_text(screenshot)

# 5. 等 swipe 完成
thread.join(timeout=5)
```

## 漂移补偿（Drift Compensation）

截图发生在 swipe 中途（1400ms / 3000ms ≈ 47%），之后手指还会继续移动，地图跟着偏移。截图里建筑的位置和最终松手后的位置**不一致**，需要补偿。

### 补偿公式

```python
remaining = 1.0 - (screenshot_delay_ms / hold_duration_ms)  # ≈ 0.533
drift = int(drag_offset * remaining)                          # 150 * 0.533 ≈ 80px

tap_x = bbox.x1 + tap_offset_x + drift
tap_y = bbox.y1 + tap_offset_y + drift
```

最终点击坐标 = OCR 检测到的 bbox 左上角 + 固定偏移（名称标签到建筑中心的距离）+ 漂移补偿（截图后地图还会移动的距离）。

## 导航策略：迭代式位置修正

当目标建筑不在当前视口里时，`find_and_tap`（第 162-240 行）采用迭代方式逼近：

1. **press-drag-read** — 收集所有可见建筑名称
2. **位置估算**（`_estimate_position`）— 对每个识别到的已知建筑，用"屏幕坐标 + 布局偏移"反算视口中心在城市坐标系中的位置，多个建筑取平均值
3. **计算差值** — 目标布局坐标 - 当前估算位置 = 需要滚动的 delta
4. **执行滚动**（`_scroll_by`）— 然后回到第 1 步重新检测
5. **迭代收敛** — 最多 `max_attempts` 次

### 为什么不能一次性导航？

每次 press-drag-read 本身就会轻微移动地图（拖动了 150px），位置在不断变化，必须迭代修正。

## Safe Zone 过滤

屏幕上的任务栏等 UI 也可能包含建筑名称文字（如"将兵营升至6级"）。`safe_zone` 参数定义了地图建筑名称可能出现的屏幕区域 `[x1, y1, x2, y2]`，排除 UI 区域的文字，防止位置估算被干扰。

## 并发安全

ADB swipe 在后台线程，screenshot 在主线程。这在 Nox 模拟器上验证过可以并行工作，因为它们是不同的 ADB 命令通道。

## 相关文件

| 文件 | 作用 |
|------|------|
| `vision/building_finder.py` | BuildingFinder 类，包含 press-drag-read 实现 |
| `games/<id>/game.json` → `city_layout` | 配置参数（hold_duration_ms, screenshot_delay_ms 等） |
| `docs/building_finder.md` | BuildingFinder 完整文档（含配置参数、布局格式、CLI 命令等） |
