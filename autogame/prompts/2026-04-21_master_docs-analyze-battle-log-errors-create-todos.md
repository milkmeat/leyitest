# Prompt Record

- Date: 2026-04-21 18:00
- Branch: master
- Commit: docs: 分析对战日志错误并创建 5 个 todo 修复计划

---

### 1

检查logs/ 下面的日志，看看在对战过程中有哪些报错。分类别统计各自出现的数量

> **Insight**
> 1. **最大问题是 rally_id 缺失（52次）**：AI 下达 `LVL_JOIN_RALLY` 指令时没有提供有效的 `rally_id`，说明 L1 层的 prompt 或数据感知层没有把当前可加入的集结 ID 传递给 AI。这是一个 L1 prompt / perception 层的 bug。
> 2. **指令降级为移城（127次）**：L0 执行层在处理 `LVL_ATTACK_BUILDING` 和 `LVL_REINFORCE_BUILDING` 时，如果账号距离目标太远，会自动降级为先移城。这不是错误，而是 L0 的"先移城再行动"策略。但这意味着 AI 的攻击/驻防指令在当轮并未真正执行，需要等下一轮。
> 3. **攻击友方（ret_code=28003，20次）**：AI 把友方目标当成了敌方来攻击，说明 L1 的敌我识别或建筑归属判断有问题。
> 4. **error=-161 是城墙状态推送的附带信息**，出现在几乎所有移城操作后，可能是服务器端城墙数据同步的已知行为，不影响移城本身的成功。
> 5. **队列占用（queueid occupied）** 说明 AI 没有正确感知账号当前的出征槽位状态，向已经满槽的账号下达了出征指令。

### 2

将这些问题分成独立的todo文件，记录到 todo/ 目录下，准备后续分别处理。文件格式可以参考todo_template.md

> **Insight**
> 1. **建议优先处理前两个**：rally_id 缺失（52次）和攻击友方（20次）是纯逻辑 bug，修复后能直接减少约 60% 的失败。队列占用和坐标无效属于边界校验问题，修复难度较低。
> 2. **最后一个是优化项而非 bug**：指令降级是 L0 的容错设计在正常工作，但 29% 的降级率说明 L1/L2 的距离感知不足，值得后续优化。

**Files:** `todo/fix_join_rally_missing_rally_id.md`, `todo/fix_attack_ally_target.md`, `todo/fix_queue_occupied_awareness.md`, `todo/fix_reinforce_building_invalid_coords.md`, `todo/investigate_action_downgrade_to_move_city.md`
