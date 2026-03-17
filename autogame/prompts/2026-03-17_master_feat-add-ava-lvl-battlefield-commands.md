# Prompt Record

- Date: 2026-03-17 18:00
- Branch: master
- Commit: feat: add AVA battlefield (lvl_*) commands to config, game_api, and l0_executor

---

### 1. 从 lvl yaml 添加新命令字到系统

从cmd_config.lvl.yaml中把新增加的命令字添加到系统中。已有的不需要变更

> **Insight**
> 1. 命令字命名空间分层设计：新增的 lvl_* 命令与原有命令形成清晰的两层结构——原命令用于主世界操作，lvl_* 前缀命令用于 AVA 临时战场内操作。
> 2. 战场内的关键差异：target_type 不同（主世界用 2/13，战场内用 10101/10001/107）；集结 prepare_time 缩短（300→60秒）；新增行军加速和瞬回道具。
> 3. 对 AI 指令映射的影响：后续 L0 执行层需要根据当前是否在 AVA 战场内，自动路由到对应的 lvl_* 命令。

**Files:** `src/config/cmd_config.yaml`

### 2. 添加 Python 层对应的命令和函数

python层对应的命令和函数也加一下

> **Insight**
> 1. 主世界 vs AVA 战场的对称设计：AVA 战场的 LVL_* 指令与主世界指令形成镜像关系，但 AVA 把「攻击」拆成了 ATTACK_PLAYER 和 ATTACK_BUILDING 两个独立指令，让 L1 LLM 的输出更明确。
> 2. AVA 独有的三个操作：LVL_SPEED_UP（行军加速道具）、LVL_RECALL_TROOP（瞬回道具）、LVL_RECALL_FROM_BUILDING（从据点撤离）在主世界没有对应项。
> 3. Rally 回填机制的扩展：execute_batch 中的 rally_id 自动回填现在同时支持主世界和 AVA 的集结流程。

**Files:** `src/executor/game_api.py`, `src/executor/l0_executor.py`
