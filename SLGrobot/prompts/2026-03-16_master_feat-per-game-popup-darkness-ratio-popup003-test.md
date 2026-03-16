# Prompt Record

- Date: 2026-03-16 13:19
- Branch: master
- Commit: feat: add per-game popup_darkness_ratio + frozenisland popup_003 test

---

### 1. Add screenshot test

add screenshot test

> **Insight**
> 这个项目使用截图+模板匹配来识别游戏场景，添加截图测试用例是验证视觉识别准确性的关键步骤。

**Files:** `tests/screenshots/frozenisland/popup_003.png`, `tests/screenshots/frozenisland/popup_003.yaml`

### 2. Confirm YAML config for popup_003

> **Q:** 这个首充奖励弹窗的测试用例配置是否正确？场景: popup, 自动动作: 点击 close_x.2 关闭。需要调整吗？

确认，直接保存

**Files:** `tests/screenshots/frozenisland/popup_003.png`, `tests/screenshots/frozenisland/popup_003.yaml`

### 3. Choose fix approach for PopupDetector threshold

> **Q:** PopupDetector 的亮度对比无法识别这个弹窗。你希望怎么处理？

单独为fronzenisland调整阈值，使之匹配为popup。预期行为应该是点击close_x

> **Insight**
> 1. **每游戏独立阈值模式**：与 `template_match_threshold` 和 `finger_ncc_threshold` 一样，`popup_darkness_ratio` 现在也支持在 `game.json` 中按游戏独立配置，`0.0` 表示使用类默认值 `0.5`
> 2. **为什么 0.6 有效**：这个弹窗的 `border_mean / center_mean = 85.7 / 157.8 ≈ 0.543`，原来的阈值 `0.5` 刚好卡住了。0.6 的阈值给了足够的余量，同时不会让正常的非弹窗画面被误判为弹窗
> 3. **最小侵入性修改**：通过让 `PopupDetector` 接受构造参数而非硬编码常量，保持了向后兼容——其他游戏不设置此字段就自动使用默认值

**Files:** `vision/popup_detector.py`, `game_profile.py`, `vision/screen_dom.py`, `games/frozenisland/game.json`
