# Auto Loop 自动循环模式

启动方式：

```bash
python main.py --auto              # 无限循环
python main.py --auto --loops 50   # 限制最多 50 轮
```

`auto_loop` 是一个无限循环（或受 `--loops` 限制），每次迭代执行以下决策链。按 `Ctrl+C` 可优雅退出并保存状态。

## 每次循环执行流程（按优先级排序）

| 步骤 | 操作 | 说明 |
|------|------|------|
| **0. ADB 健康检查** | 检测模拟器连接，断开则自动重连 | 最多重试 `ADB_RECONNECT_RETRIES`(3) 次，失败则停止循环 |
| **1. 截图** | `screenshot_mgr.capture()` | 连续 3 次截图失败触发 ADB 重连 |
| **2. 场景分类** | `classifier.classify(screenshot)` | 识别当前画面属于哪种场景（见下方场景列表） |
| **2a. 卡死检测** | 连续 `STUCK_MAX_SAME_SCENE`(10) 次相同场景触发恢复 | 逐步升级：按返回 → 点击中心 → 重启游戏 |
| **2c. 主城状态更新** | 在主城场景下提前提取任务栏信息 | 为后续手指检测和任务触发提供数据 |
| **2d. 教程手指检测** | 检测画面中的"引导手指"图标 | **最高优先级**，发现就直接点击手指尖位置，同时重置所有 exhaust 计数器 |
| **3. 退出对话** | `exit_dialog` → 点击"继续"按钮 (826, 843) | 暗背景容易被误判为其他场景，优先处理；点击后等待 60s |
| **3b. 英雄列表/招募** | `hero` → 点返回；`hero_recruit` → 先点 primary button 再返回 | 防止卡在英雄界面 |
| **3c. 英雄升级** | `hero_upgrade` → 有红字（资源不足）不点升级，直接返回 | 使用 `has_red_text_near_button()` 检测资源不足 |
| **4. 弹窗处理** | `popup` 场景 → 先检查奖励按钮 → primary button → 关闭弹窗 | 跳过弹窗，不让弹窗阻塞流程 |
| **4b. 剧情对话** | `story_dialogue` → 尝试点"跳过" → 点三角 → 点屏幕中心 | 自动跳过剧情 |
| **5. 加载画面** | `loading` → 检查是否有 primary button（防止误判）→ 等待 | 真正的加载画面不做操作，只等待 |
| **5b. 远征编队** | `unknown` 场景下 OCR 检测"一键上阵" → 点击 → 点击"出战" | 自动编队出征 |
| **6. 未知场景** | 尝试 back_arrow → primary button → popup filter → 3 次未知则点空白区域 | 逐级升级脱困 |
| **7. 状态更新** | 非主城场景的 `state_tracker.update()` | 主城在步骤 2c 已更新 |
| **7.5 任务奖励领取** | 主城 + 任务栏绿色对勾 → 点击领取奖励 | 自动领取已完成任务的奖励 |
| **7.6 已知弹窗横幅** | 匹配已知弹窗模板（如联盟招募）→ 关闭 | 每次迭代都检查 |
| **8. AutoHandler 决策** | `auto_handler.get_actions()` 扫描当前画面 | 寻找可做的事（收资源、领奖励等） |
| **9. 持久化** | 保存游戏状态到 `data/game_state.json` | 每次迭代结束时 |

每次迭代最后 `sleep(LOOP_INTERVAL)` (2.0s) 后进入下一轮。

## 场景类型

场景分类采用优先级瀑布检测（`SceneClassifier.classify()`）：

| 优先级 | 场景 | 检测方式 |
|--------|------|----------|
| 1 | `popup` | 屏幕边缘比中心暗（暗遮罩），且匹配到关闭/X 按钮模板 |
| 2 | `exit_dialog` | 匹配 `scenes/exit_dialog` 模板（暗背景+蓝色图标） |
| 3 | `loading` | 灰度标准差 <20（颜色均匀）或均值 <30/>240 |
| 4 | `story_dialogue` | `icons/down_triangle` 模板匹配 ≥0.9 |
| 5 | `main_city` / `world_map` | 裁剪右下角区域匹配 `scenes/` 下对应图标，阈值 ≥0.5 |
| 6 | `hero` / `hero_recruit` / `hero_upgrade` / `battle` | `scenes/` 目录全扫描匹配 |
| 7 | `unknown` | 兜底 |

## AutoHandler（步骤 8）

当所有场景特定处理器都未命中时，`AutoHandler.get_actions()` 按以下顺序扫描：

1. **已知弹窗** — 匹配标识模板，点击对应关闭模板
2. **奖励按钮** — 模板匹配 `buttons/claim` 等 + OCR 匹配"领取"等文字
3. **加载画面** — 点击屏幕中心

## Primary Button 检测

`find_primary_button()` 基于 HSV 颜色检测可点击按钮，不依赖模板或 OCR：

| 优先级 | 颜色 | 用途 |
|--------|------|------|
| 高 | 蓝色 / 绿色 | 主要动作按钮（升级、确认等） |
| 低 | 金色 | 次要按钮 |

配合 `has_red_text_near_button()` 可检测按钮附近是否有红色文字（资源不足提示），避免无效点击。

## 卡死恢复

`StuckRecovery` 在连续 `STUCK_MAX_SAME_SCENE`(10) 次相同场景时触发，逐步升级：

| 等级 | 操作 | 说明 |
|------|------|------|
| Level 1 | `key_event(4)` — 按返回键 | 最温和的退出方式 |
| Level 2 | `tap(center_x, center_y)` — 点击屏幕中心 | 尝试关闭可能的遮挡 |
| Level 3 | `force-stop` + `monkey` 重启游戏 | 最后手段 |

场景变化时调用 `reset()` 重置等级回 0。恢复后清空 `scene_history`。

## 容错机制

| 异常情况 | 处理策略 |
|---------|---------|
| **ADB 断连** | 自动重连，最多重试 `ADB_RECONNECT_RETRIES`(3) 次 |
| **截图失败** | 连续 3 次后触发 ADB 重连 |
| **卡死检测** | 连续相同场景时逐步升级恢复手段（返回 → 中心点击 → 重启） |
| **连续异常** | 5 次连续 Python 异常则终止循环 |
| **Ctrl+C** | 优雅退出，保存游戏状态 |

## 关键配置参数

| 常量 | 值 | 用途 |
|------|---|------|
| `LOOP_INTERVAL` | 2.0s | 迭代间隔 |
| `STUCK_MAX_SAME_SCENE` | 10 | 触发卡死恢复的相同场景次数 |
| `ADB_RECONNECT_RETRIES` | 3 | ADB 重连最大次数 |
| `ACTION_MAX_RETRIES` | 3 | 单个 action 执行重试次数 |
| `SCREEN_WIDTH / HEIGHT` | 1080 × 1920 | 模拟器分辨率要求 |
| `_ABORT_COOLDOWN` | 180s | quest script 中止后冷却时间 |

## 相关代码

- 主循环：`main.py` — `GameBot.auto_loop()`
- 场景分类：`scene/classifier.py` — `SceneClassifier.classify()`
- 弹窗过滤：`scene/popup_filter.py` — `PopupFilter.handle()`
- Primary Button：`scene/classifier.py` — `find_primary_button()` / `has_red_text_near_button()`
- 自动处理：`brain/auto_handler.py` — `AutoHandler.get_actions()`
- 任务脚本：`brain/quest_script.py` — `QuestScriptRunner`
- 卡死恢复：`brain/stuck_recovery.py` — `StuckRecovery.check()` / `recover()`
- 执行管线：`executor/` — `ActionValidator` → `ActionRunner` → `ResultChecker`
