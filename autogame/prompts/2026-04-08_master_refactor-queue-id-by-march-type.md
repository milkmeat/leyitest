# Prompt Record

- Date: 2026-04-08 00:00
- Branch: master
- Commit: refactor: 按行军类型分配队列 ID（solo=6001, 集结=6002, 采集=6003）

---

### 1. 按行军类型分配默认队列 ID

修改一下：
1. solo行军默认使用队列queueId=6001
2. 发起与参加集结默认使用队列queueId=6002
3. 采集矿车默认使用队列queueId=6003 (已实现)

> **Insight**
> 用不同队列 ID 区分行军类型是 SLG 常见设计：服务器用 queueId 做并发槽位管理。6001 管 solo 出征，6002 管集结，6003 管采集，互不占用对方的槽位。这样一个账号可以同时有 solo 行军 + 集结行军 + 采集行军各一支。

> **Insight**
> 在 l0_executor.py 中用集合 _RALLY_ACTIONS 集中判断而非在每个分支里硬编码 queue_id，这样新增集结类型时只需往集合里加一项，不用到处改数字。

**Files:** `src/executor/l0_executor.py`, `src/main.py`, `src/config/cmd_config.yaml`
