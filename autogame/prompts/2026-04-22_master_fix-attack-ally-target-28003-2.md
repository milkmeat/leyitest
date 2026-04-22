# Prompt Record

- Date: 2026-04-22 17:55
- Branch: master
- Commit: fix: 消除攻击友方目标 28003 错误（实时归属查询+L1 prompt 增强，20→0）

---

### 1. 审计 todo 修复状态

检查logs/下的最新日志，对照 @todo\ 下的md文件（不包括done），看看是否主要问题都修复了。

> **Insight**
> 日志分析的关键发现：
> - L0 预检机制是这批修复的核心模式 — 在发送到服务器前拦截无效指令，避免浪费网络请求
> - 28003 错误有两种语义：一种是"攻击友方玩家"（原始 bug），另一种是"对已占领建筑发起集结"（建筑归属变化导致）。最新日志中出现的是后者
> - RECALL 的 30001 错误是独立问题，与 queue occupied 修复无关

### 2. 按最新 todo 完成修复

> **Q:** 代码修改已完成。回归测试需要运行 ava_simulate.sh（默认 20 分钟）。你想怎么做？

我修改了 fix_attack_ally_target.md，按最新版本完成该修复

> **Insight**
> 根因分析完成：
> - `l1_view.py` 建筑归属逻辑正确（line 334-339: 用 `alliance_id` 对比 `_my_alliance_id`）
> - `data_sync.py` 每轮 Phase 1 都会刷新建筑数据（`_sync_map_ava` → `svr_lvl_brief_objs`）
> - L1 prompt (`l1_system_ava.txt:35`) 已有规则："Our building → REINFORCE, NOT ATTACK"
> - L0 已有 INITIATE 预检查（line 445-481）和 28003 恢复机制（line 559-599）
> - **真正的 gap**: L1/L2 思考耗时 ~150s，期间建筑归属可能变化，sync 缓存过时

> **Insight**
> Fix 6 的设计思路：
> - 问题本质是 **时间差**：sync 数据在 Phase 1 获取，但 action 在 Phase 4 执行，中间 ~150s 的 L1/L2 思考时间内建筑归属可能变化
> - 已有的 Fix 4（缓存预检查）和 28003 恢复机制是"事后补救"，Fix 6 是"事前预防"
> - 实现方式：在 INITIATE_RALLY / ATTACK_BUILDING 执行前，对缓存中标记为"敌方"的建筑做一次轻量级服务器查询，获取最新 alliance_id
> - 代价：每个 INITIATE/ATTACK 多一次 API 调用（每轮约 4-8 次），换取消除 28003 错误

**Files:** `src/executor/l0_executor.py`, `src/ai/prompts/l1_system_ava.txt`, `todo/fix_attack_ally_target.md`

### 3. 选择运行完整回归测试

> **Q:** 代码修改已完成。回归测试需要运行 ava_simulate.sh（默认 20 分钟）。你想怎么做？

运行 ava_simulate.sh 20

> **Insight**
> 回归测试结果分析：
> - **28003 错误：20 → 0**（完全消除）
> - Fix 6 实时归属查询未被触发（0 次），说明本轮测试中没有出现 sync→action 时间差导致的归属变化。28003 的消除主要得益于已有的 Fix 4 缓存预检查 + "已是我方转 REINFORCE" 机制（触发 4 次）
> - 总体成功率 248/(248+80) = 76%，主要失败原因是 queue occupied SKIP（68 次），这是 L1 队列感知不足的问题，不在本次修复范围内
