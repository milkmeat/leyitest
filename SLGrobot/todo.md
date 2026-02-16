# SLGrobot TODO

Phase 1-5 框架已完成，以下是后续工作方向。

---

## 最优先：实际游戏适配

### 1. 填充模板库
- [x] 21个模板已截取并手工校准
- [x] `buttons/`: back_arrow, close_x, recruit_more, view
- [x] `icons/`: event_daily, event_journey, event_recharge, member_badge, regular_activity, task_scroll
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

## 进阶功能

### 6. 扩充 Rule Engine 规则
- [ ] 根据实际游戏玩法添加更多任务规则
- [ ] 覆盖日常任务流程：采集、训练、研究、联盟帮助等
- [ ] 处理特殊事件：战争、活动、限时任务

### 7. LLM Prompt 调优
- [ ] 根据实际游戏截图调整 prompt 模板
- [ ] 优化 LLM 对场景的理解准确率
- [ ] 减少不必要的 LLM 调用，降低成本
- [ ] 测试不同模型（Claude / GPT / 本地模型）效果对比

### 8. 多账号/多实例支持
- [ ] 支持同时操控多个 Nox 模拟器实例
- [ ] 每个实例独立的 ADB 端口和状态
- [ ] 统一调度和资源分配

### 9. Web Dashboard
- [ ] 远程监控 bot 运行状态
- [ ] 实时查看截图和日志
- [ ] 远程启停和参数调整
- [ ] 统计面板：运行时长、任务完成数、恢复次数等
