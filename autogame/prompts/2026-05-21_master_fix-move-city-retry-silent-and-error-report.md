# Prompt Record

- Date: 2026-05-21 15:05
- Branch: master
- Commit: fix: LVL_MOVE_CITY 重试静默化 + 彻底失败时完整错误报告

---

### 1

看一下 logs/ 目录下的模拟日志，统计 LVL_MOVE_CITY 出错时的发生次数、发生场景、发生原因

> **Insight**
> **日志架构的盲区**：`_build_l0_log` 记录的是 L1 原始指令 + `execute_batch` 返回的最终结果（一一对应）。但 L0 内部的预处理链（ATTACK→MOVE_CITY→重试→追击）中间步骤全部丢失。
>
> **为什么 21105 错误不在 JSON 日志中**：
> 1. L1 生成 `LVL_ATTACK_BUILDING` 指令
> 2. L0 预处理发现距离 > 阈值，转换为 `LVL_MOVE_CITY`
> 3. 移城失败（21105: 目标位置被占），触发 `_retry_move_city`
> 4. 重试成功 → 追击原始攻击 → 最终 result 覆盖为攻击结果
> 5. 重试全部失败 → 最终 result 是 "移城重试全部失败" 的 ExecutionResult
>
> 但 JSON 日志的 instruction 字段记录的是**原始 L1 指令**（LVL_ATTACK_BUILDING），而 result 字段记录的是**最终结果**。中间的每次 21105 失败尝试（包括 smart 搜索和 random 偏移）都只通过 `logger.warning` 输出到控制台，不进入 JSON。

### 2

在cli运行过程中，控制台会打印出以下的错误信息，是不是这类warning没有记录在logs里面

Response: {"res_header": {"ret_code": 21105, "cost_time_us": 0, "ret_time_s": 1779340408, "err_msg": ""}, "request": {"header": {"aid": 20000118, "battle_id": 0, "battle_type": 0, "castle_lv": 25, "chat_scene": ",kingdom_1", "did": "self-system", "invoker_name": "ying_test_debug", "ksid": 1, "lvl_id": 40002, "sid": 1, "uid": 20010683}, "request": {"cmd": "lvl_move_city", "param": {"use_gem": 1, "item_id": 1, "tar_pos": 11900012200}}, "extra_info": {"no_checkac": 1, "op_cmd": 1}}, "res_data": []}
13:13:28 [src.executor.l0_executor] WARNING: L0 服务器返回错误: LVL_MOVE_CITY uid=20010683 —  (Please move your Haven to an open space.)
13:13:28 [src.executor.game_api] WARNING: [业务失败] cmd_name=lvl_move_city cmd=lvl_move_city uid=20010683 code=21105

### 3

LVL_MOVE_CITY 会重试3次对吗？如果中间重试但最终成功了，不需要打印任何warning到控制台或log。但是如果全部重试都失败，彻底无法移城时，需要打印到控制台和log，包括出错时的发生次数、发生场景（初始指令是什么）、发生原因

> **Insight**
> **关键设计选择**：
> 1. `silent` 用 keyword-only 参数（`*` 后面），避免与现有的 `rally_pos` 位置参数冲突，所有现有调用无需修改
> 2. 中间重试的 `logger.info` → `logger.debug`：成功时完全静默，但如果开启 DEBUG 级别仍可追踪
> 3. `last_error` 变量贯穿整个重试链，确保最终报告包含最后一次失败的具体原因（如 ret_code=21105）

**Files:** `src/executor/l0_executor.py`
