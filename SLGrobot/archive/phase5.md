# Phase 6: Game-Specific Adaptation — Progress Report

## Overview

Phase 1-5 框架搭建完成后，进入实际游戏适配阶段。目标游戏：**冰封家园 (Frozen Island Pro)**，包名 `leyi.frozenislandpro`。

---

## 已完成

### 1. GAME_PACKAGE 配置
- 通过 ADB `dumpsys window` 获取包名 `leyi.frozenislandpro`
- 写入 `config.py`，Phase 5 的应用重启恢复（force-stop + monkey）可正常工作

### 2. 模板库建立（21个模板）

从实际游戏截图中截取并手工校准：

| 目录 | 数量 | 模板 |
|------|------|------|
| `buttons/` | 4 | back_arrow, close_x, recruit_more, view |
| `icons/` | 6 | event_daily, event_journey, event_recharge, member_badge, regular_activity, task_scroll |
| `nav_bar/` | 7 | expedition, hero, shop, supplies, territory, tribe, world |
| `scenes/` | 4 | hero, hero_recruit, main_city(世界图标), world_map(领地图标) |

### 3. Scene Classifier 重写

**旧方案**：颜色启发式（绿色比例判世界地图、饱和度判主城）— 不可靠，游戏地图可拖动导致内容变化。

**新方案**：右下角图标判定
- 右下角出现"世界"图标 → `main_city`
- 右下角出现"领地"图标 → `world_map`
- 都不是 → 检查其他 scenes/ 模板（hero, hero_recruit 等）
- 判定优先级：popup > loading > 右下角图标 > 其他模板 > unknown

实测：主城截图识别为 `main_city`，置信度 1.000。

### 4. 弹窗处理机制重构

**问题**：游戏弹窗不会变暗整个屏幕，且弹窗和功能对话框使用相同的 X 关闭按钮，不能盲目点 close_x。

**解决方案**：内容识别策略（KNOWN_POPUPS）
- 先匹配弹窗**内容特征**（identifier template）
- 确认是已知弹窗后，再找对应关闭按钮点击
- 目前已配置：联盟招募消息（检测到"查看"按钮 → 点击 close_x）

验证结果：
- 有招募弹窗的截图：正确检测并定位 close_x (1000, 1428)，置信度 1.0
- 干净主城截图：不误触发（buttons/view 未匹配）

扩展方式：在 `auto_handler.py` 的 `KNOWN_POPUPS` 列表中添加 `(识别模板, 关闭模板)` 元组即可。

### 5. 首次 Auto Loop 实跑

`python main.py --auto --loops 3` 结果：
- **Loop 1**：识别 main_city → 无 tasks → 触发 LLM 咨询（GLM-4V）→ 返回 3 个任务
- **Loop 2**：识别 main_city → 执行 close_popup 任务 → rule_engine 用 fallback 点击
- **Loop 3**：识别 main_city → 执行 claim_rewards → 找不到对应动作，任务标记失败
- 无 crash，无 stuck recovery，日志正常输出 .log + .jsonl

---

## 已知问题

1. **LLM 返回的模板名编码问题**：GLM-4V 返回中文模板名（如"关闭"），但模板文件名是英文，导致 template_matcher 找不到
2. **rule_engine 规则不足**：claim_rewards 等任务缺少对应规则，执行失败
3. **弹窗类型覆盖不全**：目前只处理联盟招募消息，其他弹窗类型待补充

---

## 下一步

### 待完成的适配工作
- [ ] 补充更多弹窗类型到 KNOWN_POPUPS
- [ ] 补充战斗、建筑升级等场景模板
- [ ] 30分钟长时间运行测试
- [ ] 验证 ADB 断连恢复和卡死恢复

### 待开发的功能
- [ ] 扩充 Rule Engine 规则（采集、训练、研究等日常任务）
- [ ] LLM Prompt 调优（模板名映射、减少无效调用）
- [ ] 多账号/多实例支持
- [ ] Web Dashboard 远程监控

---

## 文件变更清单

| 文件 | 变更 |
|------|------|
| `config.py` | GAME_PACKAGE 设为 leyi.frozenislandpro |
| `scene/classifier.py` | 重写为右下角图标判定，删除颜色启发式 |
| `brain/auto_handler.py` | KNOWN_POPUPS 内容识别策略替代盲目 close_x |
| `vision/template_matcher.py` | 添加 count() 方法 |
| `templates/**` | 新增 21 个模板文件（4个目录） |
| `todo.md` | 新增，已完成项标记 [x] |
