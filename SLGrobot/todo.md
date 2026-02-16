# SLGrobot TODO

Phase 1-5 框架已完成，以下是后续工作方向。

---

## 最优先：实际游戏适配

### 1. 填充模板库
- [ ] `templates/` 目录当前为空，需要对着实际游戏逐个截取
- [ ] 场景特征模板：主城、世界地图、弹窗、加载画面等
- [ ] 按钮模板：确定、取消、关闭、收集、训练等常用按钮
- [ ] 使用 `capture_template <category> <name> <x1>,<y1> <x2>,<y2>` 命令截取
- [ ] 建议分类目录：`scenes/`, `buttons/`, `icons/`, `popups/`

### 2. 设置 GAME_PACKAGE
- [ ] 在 `config.py` 中填写 `GAME_PACKAGE`（Android 包名）
- [ ] 可通过 `adb shell dumpsys window | grep mCurrentFocus` 获取
- [ ] Phase 5 的应用重启恢复依赖此配置

### 3. 校准 Scene Classifier
- [ ] 为每个场景提供特征模板（主城、世界地图、各建筑界面、弹窗等）
- [ ] 测试分类准确率，调整 `TEMPLATE_MATCH_THRESHOLD`
- [ ] 对误分类场景补充模板或调整分类逻辑

### 4. 实际30分钟跑测
- [ ] `python main.py --auto` 连接真实游戏
- [ ] 观察 `logs/` 下的 `.jsonl` 结构化日志和 `logs/screenshots/` 截图
- [ ] 记录失败点，迭代修复
- [ ] 验证 ADB 断连恢复、卡死恢复是否正常触发

---

## 进阶功能

### 5. 扩充 Rule Engine 规则
- [ ] 根据实际游戏玩法添加更多任务规则
- [ ] 覆盖日常任务流程：采集、训练、研究、联盟帮助等
- [ ] 处理特殊事件：战争、活动、限时任务

### 6. LLM Prompt 调优
- [ ] 根据实际游戏截图调整 prompt 模板
- [ ] 优化 LLM 对场景的理解准确率
- [ ] 减少不必要的 LLM 调用，降低成本
- [ ] 测试不同模型（Claude / GPT / 本地模型）效果对比

### 7. 多账号/多实例支持
- [ ] 支持同时操控多个 Nox 模拟器实例
- [ ] 每个实例独立的 ADB 端口和状态
- [ ] 统一调度和资源分配

### 8. Web Dashboard
- [ ] 远程监控 bot 运行状态
- [ ] 实时查看截图和日志
- [ ] 远程启停和参数调整
- [ ] 统计面板：运行时长、任务完成数、恢复次数等
