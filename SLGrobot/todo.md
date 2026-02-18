# SLGrobot TODO

Phase 1-5 框架已完成，Phase 6 Quest Workflow 已实现，以下是后续工作方向。

---

## 最优先：实际游戏适配

### 1. 填充模板库
- [x] 21个模板已截取并手工校准
- [x] `buttons/`: back_arrow, close_x, recruit_more, view
- [x] `icons/`: event_daily, event_journey, event_recharge, member_badge, regular_activity, task_scroll, tutorial_finger
- [x] `nav_bar/`: expedition, hero, shop, supplies, territory, tribe, world
- [x] `scenes/`: hero, hero_recruit, main_city, world_map
- [ ] 继续补充：更多弹窗类型、战斗界面、建筑界面等

### 2. 设置 GAME_PACKAGE
- [x] `GAME_PACKAGE = "leyi.frozenislandpro"` 已设置
- [x] Phase 5 应用重启恢复可正常工作

### 3. 校准 Scene Classifier
- [x] 主城/世界地图：通过右下角图标判定（"世界"=主城，"领地"=世界地图）
- [x] 删除不靠谱的颜色启发式方法
- [x] 实测验证：主城截图识别为 main_city，置信度 1.0
- [ ] 补充更多场景模板（战斗、建筑升级界面等）
- [ ] 在不同游戏状态下测试分类准确率

### 4. 弹窗处理
- [x] 改为内容识别策略：先匹配弹窗特征，再找关闭按钮
- [x] 联盟招募消息：检测"查看"按钮 → 点击 close_x 关闭
- [x] 干净画面不误触发（已验证）
- [ ] 添加更多弹窗类型到 `KNOWN_POPUPS` 列表

### 5. 实际跑测
- [x] `python main.py --auto --loops 3` 首次跑通，无 crash
- [x] 场景识别正常（3轮均正确识别 main_city）
- [x] LLM 集成正常（GLM-4V 成功返回任务）
- [x] 日志输出正常（.log + .jsonl）
- [ ] 30分钟长时间运行测试
- [ ] 验证 ADB 断连恢复
- [ ] 验证卡死恢复

---

## Phase 6: Quest Workflow（已完成）

### 6. Quest Bar 检测 + Quest Workflow 状态机
- [x] `vision/quest_bar_detector.py` — QuestBarDetector + QuestBarInfo
- [x] `brain/quest_workflow.py` — 8 阶段状态机（IDLE → ENSURE_MAIN_CITY → READ_QUEST → CLICK_QUEST → EXECUTE_QUEST → CHECK_COMPLETION → CLAIM_REWARD → VERIFY）
- [x] `brain/llm_planner.py` — analyze_quest_execution() + QUEST_EXECUTION_PROMPT
- [x] `state/game_state.py` — quest bar 状态字段 + workflow 持久化字段
- [x] `state/state_tracker.py` — 主城更新时调用 _update_quest_bar()
- [x] `brain/auto_handler.py` — CLAIM_TEXT_PATTERNS 增加 "一键领取"
- [x] `main.py` — auto_loop 接入 Workflow + popup 领奖优先
- [x] `icons/tutorial_finger.png` — 手指引导模板
- [x] `test_quest_workflow.py` — 37 个单元测试全部通过
- [x] `docs/workflow_complete_current_quest.md` — 文档更新

### 7. Quest Workflow 实跑验证
- [x] `python main.py --auto --loops 30` 观察 quest workflow 日志
- [x] 确认卷轴模板匹配在不同游戏状态下稳定（重新截取 task_scroll 模板，conf=1.0）
- [x] 确认 OCR 正确读取 quest 文本（中文）
- [x] 确认 tutorial_finger 模板匹配有效（含左右镜像检测）
- [x] 测试 quest 执行完整循环（建筑升级任务成功完成）
- [ ] 确认红色徽标 / 绿色对勾 HSV 阈值准确（待更多场景验证）

---

## Phase 7: 弹窗修复与脱困（已完成）

### 8. 模板匹配 Alpha 透明遮罩支持
- [x] `vision/template_matcher.py` — cache 改为 `(bgr, mask)` 元组，加载保留 alpha 通道
- [x] 有 mask 时使用 `TM_CCORR_NORMED`，无 mask 时保持 `TM_CCOEFF_NORMED`
- [x] `templates/buttons/close_x.png` — HSV 颜色分割提取红色 X，非红色区域透明化
- [x] close_x 可在不同背景色对话框上匹配

### 9. close_popup 三阶段安全策略
- [x] `brain/rule_engine.py` — `_plan_close_popup()` 改为三阶段：
  - 阶段 1: 仅 template 匹配 close 类按钮模板
  - 阶段 2: 仅 OCR 搜索多字符文本（避免单字符 "X"/"×" 误匹配）
  - 阶段 3: 兜底按 BACK 键（keycode=4）
- [x] 解决了 OCR 搜索 "X" 误触聊天入口的问题

### 10. Unknown 场景 BACK 键脱困
- [x] `main.py` — 添加 `consecutive_unknown_scenes` 计数器
- [x] 连续 3 次 unknown 场景后自动按 BACK 键脱出
- [x] 非 unknown 场景重置计数器

### 11. Quest Workflow 实战修复
- [x] Tutorial finger 指尖偏移修正（`_FINGERTIP_OFFSET = (-65, 100)`）
- [x] Tutorial finger 左右镜像检测与处理
- [x] 建筑升级按钮检测：模板匹配优先 → OCR 回退
- [x] 连续点击家具升级（`_RAPID_TAP_COUNT = 15`）
- [x] 新增模板：`buttons/upgrade_building.png`, `buttons/build.png`
- [x] 重新截取 `icons/task_scroll.png`（旧模板 conf=0.771，新模板 conf=1.0）
- [x] Red badge 不再误触卷轴打开任务面板

## Phase 8: LLM 调试日志与 Quest Workflow 加固（已完成）

### 12. LLM 调试日志
- [x] LLM 响应原始 JSON 写入 `.jsonl` 日志
- [x] LLM 调用耗时、token 用量记录

### 13. Quest Workflow 弹窗 OCR 关闭
- [x] `_step_execute_quest` popup 处理：OCR 搜索 "返回领地"、"确定" 等文本
- [x] 从 OCR dismiss 列表中移除 "领取"（避免误触领取按钮）

---

## Phase 9: 弹窗处理全面加固与 Quest Workflow 鲁棒性（已完成）

### 14. Quest Workflow 优先级修复
- [x] `main.py` — Quest Workflow 启动检查移到 Step 7.5（在 TaskQueue 和 LLM 咨询之前）
- [x] 解决了 LLM 生成的任务抢占 quest workflow 导致远征任务无法执行的问题

### 15. 按钮优先级与单按钮修复
- [x] `_ACTION_BUTTON_TEXTS` 新增 "开始战斗"（高优先级，index 2）
- [x] "领取" 移到最低优先级（列表末尾）
- [x] `_find_action_buttons` 只返回最高优先级的一个按钮，避免同时点击多个按钮

### 16. 弹窗逐级升级机制
- [x] `_step_execute_quest` popup 处理增加 `popup_back_count` 计数器
- [x] 升级策略：OCR 文本 → close_x 模板 → BACK×2 → 屏幕中心×2 → LLM 分析 → 兜底中心点击
- [x] `_step_return_to_city` 完整重写，增加与 execute_quest 相同的弹窗升级逻辑
- [x] 解决了 return_to_city 阶段遇弹窗只按 BACK 无法关闭的问题

### 17. close_x 假阳性过滤
- [x] 所有 close_x 模板匹配增加位置验证（右上角区域：y < 35%, x > 45%）
- [x] `scene/popup_filter.py` — close_x 位置验证
- [x] `brain/quest_workflow.py` — execute_quest 和 return_to_city 两处 close_x 位置验证
- [x] 解决了红色 X 模板在主城、战斗结果等界面的大量假阳性问题

### 18. Popup Filter OCR 优先
- [x] `scene/popup_filter.py` — 策略重排：OCR 文本搜索优先于模板匹配
- [x] 解决了失败弹窗上 close_x 误匹配 ">" 箭头导致无限循环的问题

### 19. Unknown 场景 Popup Filter 回退
- [x] `main.py` — unknown 场景处理增加 popup_filter 尝试（在 LLM 调用之前）
- [x] 处理 "首充奖励" 等全屏弹窗（无暗色边框，被分类为 unknown 而非 popup）

### 20. 执行迭代上限增加
- [x] `max_execute_iterations` 从 20 增加到 40
- [x] 远征任务需要多轮战斗，每轮约 6 次迭代

### 21. 全屏弹窗 close_x 检查（execute_quest 内）
- [x] LLM 回退之前增加 close_x 模板检查（带位置验证）
- [x] 在 quest workflow 内部也能关闭 "首充奖励" 等 unknown 分类的全屏弹窗

---

## 已知问题与待解决

### close_x 模板局限性
- close_x（红色 X）模板匹配假阳性率高，已通过位置验证（右上角）缓解
- 场景分类器不再单独依赖 close_x 判定 popup（需暗色边框配合）
- "首充奖励"等全屏弹窗无暗色边框，通过 unknown → popup_filter 路径处理

### 远征战斗
- 远征第 10 关需要多轮战斗，bot 可能战力不足导致失败
- 失败后出现 "失败" 弹窗，已通过 OCR 找到 "返回领地" 正确处理
- 如果反复失败，workflow 会在 max_execute_iterations 后退出

### 日志中文乱码
- Windows 终端日志中中文显示为乱码（如 `ͨ��Զ����10�ء�`）
- 功能不受影响，但调试不便
- 日志文件（.log/.jsonl）中中文正常

---

## 进阶功能

### 8. 扩充 Rule Engine 规则
- [ ] 根据实际游戏玩法添加更多任务规则
- [ ] 覆盖日常任务流程：采集、训练、研究、联盟帮助等
- [ ] 处理特殊事件：战争、活动、限时任务

### 9. LLM Prompt 调优
- [ ] 根据实际游戏截图调整 prompt 模板
- [ ] 优化 LLM 对场景的理解准确率
- [ ] 减少不必要的 LLM 调用，降低成本
- [ ] 测试不同模型（Claude / GPT / 本地模型）效果对比

### 10. 多账号/多实例支持
- [ ] 支持同时操控多个 Nox 模拟器实例
- [ ] 每个实例独立的 ADB 端口和状态
- [ ] 统一调度和资源分配

### 11. Web Dashboard
- [ ] 远程监控 bot 运行状态
- [ ] 实时查看截图和日志
- [ ] 远程启停和参数调整
- [ ] 统计面板：运行时长、任务完成数、恢复次数等
