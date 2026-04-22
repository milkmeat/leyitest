# Prompt Record

- Date: 2026-04-22 00:30
- Branch: master
- Commit: fix: 消除攻击友方目标 28003 错误（29→4，缓存修正+3层防御）

---

### 1. 检查 fix_attack_ally_target 是否已修复

我们已经完成了 fix_join_rally_missing_rally_id.md, 检查一下logs/ 的日志,看看 fix_attack_ally_target.md 是不是已经被处理了

> **Insight**
> 28003 错误（"The target is your ally"）的核心问题是**数据同步时差**：建筑被己方占领后，L1 视图仍将其标记为 `Neutral`，导致 AI 继续攻击己方建筑。这是 SLG 游戏中常见的"脏读"问题——决策层看到的世界状态落后于服务器实际状态。

> **Plan**
> 修改方案（3 层防御 + 缓存修正）：
> 1. `_mark_building_as_ours()` 缓存失效修正 — 28003 后更新 `_buildings` 缓存
> 2. Fix 1 增加缓存更新调用 — INITIATE 28003 恢复时同步更新
> 3. Fix 5: `LVL_ATTACK_BUILDING` 28003 恢复 — 转为 `LVL_REINFORCE_BUILDING` 重试
> 4. `_preprocess_lvl_attack_building` 归属预检查 — 缓存中己方建筑直接转驻防
> 5. L1 基础 prompt 补充 "我方建筑→驻防" 规则
>
> 防御层级：
> - Layer 1 (L1 Prompt) — LLM 不生成对 "Ours" 建筑的攻击指令
> - Layer 2 (L0 Pre-check) — _preprocess 拦截 ATTACK→REINFORCE
> - Layer 3 (28003 Recovery) — 服务器拒绝后转 REINFORCE + 更新缓存
> - Cache Fix — 一次 28003 修正缓存，同批次后续命令全部拦截

> **Insight**
> 这个 bug 是 SLG 游戏中经典的**读-写时差**问题：决策基于快照，但执行时世界已变。修复策略采用"乐观锁 + 回滚"思路——先尝试执行，失败后更新缓存并转换操作。关键创新点是 `_mark_building_as_ours()` 的**批次内缓存修正**：一次 28003 就能保护同批次所有后续命令，避免 N 次重复失败。

**Files:** `src/executor/l0_executor.py`, `src/ai/prompts/l1_system.txt`

### 2. 执行修改并测试

> **Q:** Plan mode 完成，是否执行修改？

执行修改。完成后使用 " ./ava_simulate.sh 39996 20 >/dev/null"，来测试. 检查 logs/ 目录验证结果

> **Insight**
> 关键观察：之前每个 loop 有多个 28003 错误（同一建筑被多个命令重复攻击），现在每个 loop 最多 1 个。这证明 `_mark_building_as_ours()` 的缓存修正机制生效了——第一次 28003 后更新缓存，同批次后续命令被 Fix 4 预检查拦截。

> **Insight**
> 剩余 4 次 28003 全部是 `LVL_INITIATE_RALLY_BUILDING`——这是数据同步时差导致的不可避免的"首次命中"。要完全消除需要在执行前重新同步建筑数据，但这会增加每轮 2-3 秒延迟。当前 0.70% 的错误率在可接受范围内，且恢复机制确保后续命令不受影响。

**Files:** `src/executor/l0_executor.py`, `src/ai/prompts/l1_system.txt`
