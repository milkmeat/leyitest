# SLGrobot TODO

## v1 状态：已完成

第一版开发已完成，详细工作总结见 `CHANGELOG.md`。

已完成的核心功能：
- Phase 1-5 框架（ADB、视觉、状态、LLM、加固）
- Phase 6-9 Quest Workflow + 弹窗全面加固
- Quest Scripting 系统（JSON 驱动多步骤脚本）
- 多游戏支持（frozenisland + westgame2）
- Building Finder（滚动城市地图找建筑）
- Finger Detector（教程手指检测与假阳性过滤）

---

## v2 方向（待规划）

### 已知局限性

- **close_x 假阳性**: 已通过位置验证缓解，但非根本解决
- **远征战力不足**: 反复失败时 workflow 会在 max_execute_iterations 后退出
- **Windows 终端中文乱码**: 功能不受影响，日志文件中正常

### 功能扩展方向

- [ ] 更多 Quest 脚本覆盖（采集、训练、研究等日常任务）
- [ ] 更多弹窗类型和场景模板
- [ ] Rule Engine 规则扩充（日常任务流程）
- [ ] LLM Prompt 调优（减少无效调用，降低成本）
- [ ] 多账号/多实例支持（多模拟器并行操控）
- [ ] Web Dashboard 远程监控
- [ ] 清理遗留代码（rule_engine.py, task_queue.py 待脚本覆盖后移除）
