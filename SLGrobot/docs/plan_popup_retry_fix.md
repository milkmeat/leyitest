# Fix: Popup Close Infinite Loop

## Context

自动循环在遇到无法通过"点击外部"关闭的弹窗时，陷入无限循环。`popup_filter.handle()` 的 Strategy 4（兜底）点击 `(54, 96)` 后始终返回 `True`，但弹窗未被关闭。main.py 不追踪连续失败次数，每次都用同样的策略重试。

修复思路：复用 `consecutive_unknown_scenes` 的既有升级模式——追踪连续 popup 次数，超过阈值后升级处理策略。**不需要截图对比**，因为下一轮循环的场景分类本身就是验证。

## 修改文件

仅修改 `main.py`，`popup_filter.py` 和 `stuck_recovery.py` 不变。

## 具体改动

### 1. 添加计数器变量 (main.py ~line 422)

在 `_popup_last_primary_pos` 之后添加：

```python
consecutive_popup_scenes = 0
_POPUP_ESCALATE_THRESHOLD = 3
```

阈值 3 与 unknown scene 升级保持一致。

### 2. 重写 popup 处理块 (main.py lines 666-701)

```python
if scene == "popup":
    consecutive_popup_scenes += 1

    # Check for claimable rewards (成功 → 重置计数)
    reward_action = self.auto_handler._check_rewards(screenshot)
    if reward_action:
        logger.info("Popup: reward button found, claiming first")
        self._execute_validated_actions([reward_action], scene, screenshot)
        consecutive_popup_scenes = 0
        time.sleep(0.3)
        continue

    # Check primary button with exhaustion (成功 → 重置计数)
    primary = find_primary_button(screenshot, y_fraction=0.2)
    if primary is not None:
        pos = (primary.x, primary.y)
        if pos == _popup_last_primary_pos:
            logger.info(f"Popup: primary at {pos} same as last, closing instead")
            _popup_last_primary_pos = None
            # 不重置计数 — 弹窗还在
        else:
            logger.info(f"Popup: primary button at ({primary.x}, {primary.y}), tapping")
            self.adb.tap(primary.x, primary.y)
            _popup_last_primary_pos = pos
            consecutive_popup_scenes = 0
            time.sleep(0.3)
            continue

    # 升级：popup_filter 已失败多次，换用 tap_blank_area (坐标不同)
    if consecutive_popup_scenes >= _POPUP_ESCALATE_THRESHOLD:
        logger.warning(
            f"Popup stuck ({consecutive_popup_scenes}x), "
            f"escalating with tap_blank_area"
        )
        self.tap_blank_area()
        self.game_logger.log_recovery(
            "popup_escape",
            f"tap_blank_area after {consecutive_popup_scenes} consecutive popup scenes"
        )
        consecutive_popup_scenes = 0
        time.sleep(0.5)
        continue

    # 正常关闭尝试
    logger.info(f"Popup detected ({consecutive_popup_scenes} consecutive), attempting to close")
    self.popup_filter.handle(screenshot)
    time.sleep(0.3)
    continue
```

关键点：
- `tap_blank_area()` 点击 `(540, 1820)` + `(540, 100)`，与 Strategy 4 的 `(54, 96)` 完全不同
- 升级后重置计数，允许再试 3 轮 → 然后 `StuckRecovery`（10 轮阈值）接管

### 3. 在其他 `continue` 分支重置计数器

| 位置 | 原有代码 | 添加 |
|------|---------|------|
| ~line 540 | `consecutive_unknown_scenes = 0` (finger alt tap) | `consecutive_popup_scenes = 0` |
| ~line 554 | `consecutive_unknown_scenes = 0` (finger tap) | `consecutive_popup_scenes = 0` |
| ~line 787 | `consecutive_unknown_scenes = 0` (battle handler) | `consecutive_popup_scenes = 0` |
| ~line 877 | `_popup_last_primary_pos = None` (else block) | `consecutive_popup_scenes = 0` |

## 升级时间线

| 循环 | 计数 | 动作 |
|------|------|------|
| 1-2 | 1→2 | `popup_filter.handle()` — 正常 4 策略尝试 |
| 3 | 3 | 升级 → `tap_blank_area()`, 计数重置 |
| 4-5 | 1→2 | `popup_filter.handle()` 再试 |
| 6 | 3 | 升级 → `tap_blank_area()`, 计数重置 |
| 10+ | — | `StuckRecovery` Level 1→2→3 (含 app restart) |

三层防线：① 3 轮后 tap_blank_area ② 10 轮后 StuckRecovery ③ 终极重启 app

## 验证

```bash
python main.py --auto --loops 15
```
制造一个不可关闭的弹窗场景，观察日志中是否出现 `Popup stuck (3x), escalating with tap_blank_area`。
