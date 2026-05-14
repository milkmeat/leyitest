# Prompt Record

- Date: 2026-05-14 21:50
- Branch: master
- Commit: feat: Rally 集结自动移城（队长+队员距离>20格时先移城再发起/加入）

---

### 1

看一下L0代码，在发起rally时，是否只有队长会移城到目标附近。而join rally的队员不会跟着移城

> **Insight**
> 1. L0 的"距离>20自动移城"逻辑仅对 `LVL_ATTACK_BUILDING` 和 `LVL_REINFORCE_BUILDING` 生效（`_preprocess_lvl_attack_building` 方法）
> 2. `LVL_INITIATE_RALLY_BUILDING`（队长发起集结）和 `LVL_JOIN_RALLY`（队员加入集结）都不经过距离检查，不会触发自动移城
> 3. 游戏机制上集结不需要城市在目标附近——部队自行行军到集结点。但如果队员距离太远，可能赶不上 60 秒集结窗口

### 2

> **Q:** 你是想确认当前行为（纯分析），还是想为 rally 场景也加上自动移城逻辑？

为 rally 加自动移城

### 3

> **Q:** 队长（INITIATE_RALLY）是否也需要自动移城？队长发起集结后部队也需要行军到目标，如果距离远同样会慢。

队长+队员都移城

> **Insight**
> 1. 复用现有的 `_find_empty_spot` + `_retry_move_city` 模式，保持代码一致性
> 2. Rally 移城的关键区别：INITIATE 成功后还需要提取 rally_id，所以追击后的 result 必须经过现有的 rally_id 提取逻辑
> 3. 需要注意 `original_rally_instr` 和 `original_attack_instr` 是互斥的（同一条指令不会同时是 rally 和 attack）

**Files:** `src/executor/l0_executor.py`

### 4

我又运行了一遍 ./ava_simulate.sh ，请检查最新日志验证
1. 是否有优先攻占空白的中立建筑
2. rally时是否都移城了

> **Insight**
> 1. 日志架构设计：`_build_l0_log` 记录的是原始 L1 指令 + 最终执行结果的配对，L0 内部的中间步骤（移城、重试、转换）不会出现在 JSON 日志中，只在 Python logger 中可见
> 2. 验证方法：对于"隐藏"的中间操作，通过比较相邻 loop 的状态变化（城市坐标）来间接验证
