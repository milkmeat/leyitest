# Prompt Record

- Date: 2026-04-21 20:55
- Branch: master
- Commit: fix: 消除 LVL_JOIN_RALLY rally_id 空失败（52→0）

---

### 1. 分析 rally 成功 vs 失败日志

准备处理 fix_join_rally_missing_rally_id.md, 在logs/ 的日志下，也有rally成功的情况，对比一下 rally  成功vs失败 有何不同

> **Plan**
> ## 日志对比分析结论
> - 成功模式：同一小队批次内 INITIATE 成功 → L0 提取 rally_id → 自动回填给后续 JOIN → 成功
> - 失败模式 A：INITIATE 返回 28003（建筑已是我方）→ 无 rally_id 可回填 → 整批 JOIN 级联失败
> - 失败模式 B：跨小队 JOIN 无 INITIATE → 全部失败
> - 关键发现：L1 从未输出过 rally_id（100%为空），Active Rallies 从未出现在 L1 输入中
>
> ## 修复计划
> - Fix 1: INITIATE 28003 恢复机制
> - Fix 2: 确保每个小队自己发起集结（禁止跨小队 JOIN）
> - Fix 3: 填充 Active Rallies 数据
> - Fix 4: L0 预检查建筑归属

> **Insight**
> Rally 系统的核心难点在于 rally_id 的时序依赖：它只在 INITIATE_RALLY 成功后才由服务器生成，所以 JOIN_RALLY 要么依赖同批次的自动回填，要么必须从"Active Rallies"视图中获取已有的 rally_id。L1 AI 经常在两者都不满足时生成 JOIN_RALLY，导致 43% 的失败率。

**Files:** `src/executor/l0_executor.py`, `src/ai/prompts/l1_system_ava.txt`, `src/controller/loop.py`, `src/perception/data_sync.py`, `src/perception/l1_view.py`, `todo/fix_join_rally_missing_rally_id.md`

### 2. 修改 Fix 2 设计：禁止跨小队集结

> **Q:** Plan 审批时的反馈

修改fix2: 不需要跨小队参加集结（去掉此功能）。每次集结必须是由小队队长发起集结，其余队员响应
加入fix4，不要等以后再做

### 3. 运行 AVA 模拟验证

运行 "./ava_simulate.sh 39998 20 >/dev/null" ，不需要输出到标准输出, 结束后检查 logs/ 目录

### 4. 修复剩余 target=(0,0) 问题

> **Q:** 剩余 16 个 rally_id 空失败是因为 L1 输出 JOIN_RALLY 时 target=(0,0)。要修复吗？

两个都修（推荐）

> **Insight**
> Fix 5 的设计利用了一个关键观察：在同一小队的指令批次中，INITIATE 总是在 JOIN 之前。所以 last_initiate_target 在处理 JOIN 时一定已经被设置了。这个"前序信息传递"模式和 last_rally_id 的回填机制完全一致，是一种可靠的批次内状态传递方式。

**Files:** `src/executor/l0_executor.py`, `src/ai/prompts/l1_system_ava.txt`

### 5. 二次验证

yes

**Files:** (verification run, no code changes)
