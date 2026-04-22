# Prompt Record

- Date: 2026-04-22 12:00
- Branch: master
- Commit: fix: 消除 queueid occupied 错误（65→2，队列感知+预检查+回退链）

---

### 1. 分析 fix_queue_occupied_awareness 并制定修复计划

@todo\fix_queue_occupied_awareness.md , 结合当前的 logs/ 目录下日志，制定修复计划

> **Plan**
> ## 修改计划（5层，按依赖顺序）
> ### Step 1: 数据层 — 解析 user_troops 到 PlayerState.troops
> - `Troop` 模型增加 `queue_id` 字段
> - 新增 `Troop.from_user_obj()` 解析 svr_lvl_user_objs.objs[] (type=101)
> - 新增 `_sync_all_troops_ava()` 为每个账号并发查询部队状态
>   - 关键发现：`svr_lvl_user_objs` 只返回查询者自己的部队，用 first_uid 全局查询只能得到 1 个账号的数据
>
> ### Step 2: 视图层 — queue_status 替代 dispatch_slots
> - MemberView 增加 `queue_status: {6001:0/1, 6002:0/1, 6003:0/1, 6004:0/1}`
> - format_text 输出改为 `queues={6001:0,6002:0,...}`
>
> ### Step 3: L0 预检查 — 队列占用拦截 + 回退队列 + 批次内追踪
> - 通用队列预检查：dispatch 前检查 required_queue 是否 occupied
> - JOIN_RALLY 回退链：6004→6003→6002
> - 批次内 inflight 追踪：防止同批次重复消耗同一队列
> - override_queue_id 传递回退 queue_id 到 _dispatch
>
> ### Step 4: L1 Prompt 更新
> - queue_status 感知规则替代 dispatch_slots>0
>
> ### Step 5: 验证
> - 服务器 30001 occupied 从 ~65 次降到 2 次 (97% 改善)

> **Insight**
> 这个 bug 的本质是**数据管道断裂**：服务器返回的 `svr_lvl_user_objs.objs` 包含完整的部队状态（含 queueId），`data_sync.py` 也确实获取了这些数据（`user_troops`），但从未解析分发到 `PlayerState.troops`。结果是整个系统的队列感知链条全部失效——L1 视图、L2 视图、L0 预检查都依赖 `acct.troops`，而它始终是空列表。
>
> 修复策略是**5 层递进**：先接通数据管道（Step 1-2），再加硬拦截（Step 3），最后优化 LLM 决策（Step 4）。其中 Step 3 的"批次内追踪"解决了一个微妙问题——同一 loop 内第 1 条指令刚消耗了 6001 队列，第 2 条指令还不知道（因为服务器还没同步），所以需要在内存中追踪本批次已消耗的队列。
>
> 关键突破：发现 `svr_lvl_user_objs` 只返回查询者自己的部队——用 `first_uid` 做全局查询只能得到 1 个账号的数据。解决方案是为每个账号并发查询 `lvl_battle_login_get`（`_sync_all_troops_ava`）。

**Files:** `src/models/player_state.py`, `src/perception/data_sync.py`, `src/perception/l1_view.py`, `src/executor/l0_executor.py`, `src/ai/prompts/l1_system_ava.txt`, `todo/fix_queue_occupied_awareness.md`
