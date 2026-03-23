# Prompt Record

- Date: 2026-03-23 20:30
- Branch: master
- Commit: fix: AVA 集结全链路修复 (timestamp/building_id/rally_id/leader/tn_limit) + CLI 命令

---

### 1. 只处理小队1，跳过其他小队

执行这个mock测试的时候，怎么让他只处理小队1，不处理其他小队（尚未进入ava地图，无需测试）
python src/main.py --llm ollama run --once --loop.interval_seconds 0 --ava 29999 --mock-l2 "[小队 1 (Alpha)] 控制 建筑
pos:( 154, 170 )"   --l1-prompt ava_test

> **Insight**
> 当前 `decide_all()` 遍历 `self.leaders.items()`（全部10个小队），即使 mock_l2 只解析出了 `{1: "控制 建筑..."}`，其他9个小队也会被调用 LLM（带空指令）。修改点在第 230 行：当 `l2_orders` 非空时，只遍历其中有指令的小队。

**Files:** `src/ai/l1_leader.py`

### 2. 修复 timestamp 和 JOIN_RALLY rally_id 问题

都要修复。对于问题2,队长先发起集结。集结的队员应该从队长处获得rally_id

> **Q:** 要先修哪个问题？还是说你主要关心的是小队过滤这个功能点，这两个问题后续再处理？（问题1: timestamp 空字符串类型错误，问题2: JOIN_RALLY 缺少 rally_id）

> **Insight**
> 问题1 根因：`cmd_config.yaml` 第 479/506 行 `timestamp: ""` 是空字符串，YAML 默认值。服务器期望整数类型。
> 问题2 根因：`execute_batch()` 已有 rally_id 自动回填机制（282-297行），但因为问题1导致 INITIATE_RALLY 失败，`last_rally_id` 从未被赋值，后续 JOIN_RALLY 无法回填。修复问题1 后问题2 自动解决。

**Files:** `src/config/cmd_config.yaml`, `src/executor/game_api.py`

### 3. 修复 building_id 只输出数字 key 的问题

> **Q:** building_id 问题需要看 L1 prompt 给 LLM 展示的建筑数据格式。要继续查这个问题吗？

ok

> **Insight**
> 数据侧：`l1_view.py:213` 展示的是 `b.unique_id`（完整的 `10006_1773137411102403`），LLM 能看到正确的 ID。
> Prompt 侧：`l1_system_ava_test.txt:31` 示例中 `building_id: "1001"` 只是个 key 值，误导 LLM 只输出数字部分。

**Files:** `src/ai/prompts/l1_system_ava_test.txt`

### 4. 修复 target_type 从 building_id 截取

 "target_type": 10001,  这个target_type要从building_id上面截取，是10006

> **Insight**
> AVA 建筑的 `unique_id` 格式是 `{type}_{timestamp}`（如 `10006_1773137411102403`），第一段就是 target_type。之前硬编码 `10001` 是通用建筑类型，但 AVA 据点有不同类型（10000-10006），服务器需要精确匹配。`lvl_attack_building` 早就有这个截取逻辑，`lvl_create_rally_building` 漏了。

**Files:** `src/executor/game_api.py`

### 5. 添加 lvl_battle_login_get CLI 命令

cli发起lvl rally 集结用什么命令？

**Files:** `src/main.py`

### 6. 添加 lvl_create_rally CLI 命令

增加一个cli命令发起lvl集结，并且打印出完整响应

**Files:** `src/main.py`

### 7. 添加 lvl_battle_login_get CLI 支持

cli 命令行支持lvl_battle_loging_get吗?

**Files:** `src/main.py`

### 8. 实现 rally_id 查询和全链路修复

> **Q:** 现在可以用这个命令来调试。接下来你要继续解决 rally_id 的获取问题吗？

ok

> **Insight**
> 服务器响应中 push data 只包含 `svr_soldier` 等兵力数据，没有 `svr_user_objs_inc` 或 `svr_rally_info`。rally_id 不在 HTTP 响应中返回。
> 通过 `lvl_battle_login_get` 查询 `svr_lvl_user_objs`，找 type=107 的集结对象，其 `uniqueId` 就是 rally_id。
> JOIN_RALLY 的 `march_info` 中 `leader: 1`（带英雄领军），但加入集结的队员不应该带 leader。`needs_hero` 没排除 `LVL_JOIN_RALLY`。
> `tn_limit=1` 太小，只允许队长自己，队员加不进去。改为 15。

**Files:** `src/executor/l0_executor.py`, `src/executor/game_api.py`
