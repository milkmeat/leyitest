# Prompt Record

- Date: 2026-04-02 10:30
- Branch: master
- Commit: fix: AVA 集结 rally_id 查询修正 (svr_lvl_rally brief + lvl_id 判断)

---

### 1. Fix rally_id query not finding rally after INITIATE_RALLY

20010443的集结实际上已经发起成功了，看一下为什么所有队员的join 都失败

> **Insight**
> 两个问题：(1) execute_batch 中 rally_id 查询条件用 `instr.action in {LVL_INITIATE_RALLY, ...}` 判断，但经过 _AVA_ACTION_MAP 映射后 instr.action 已经变成了 INITIATE_RALLY（映射前），所以条件永远不满足。(2) _query_rally_id 从 svr_lvl_user_objs 找 type=107 的对象，但真实服务器把集结信息放在 svr_lvl_rally 的 brief 数组中，格式是 `{ownerUid, uniqueId, pos}`。修正为：查询条件改为 `lvl_id != 0`；_query_rally_id 优先查 svr_lvl_rally brief 匹配 ownerUid，回退到 svr_lvl_user_objs 的 cityInfo.mainTroopUniqueId。

**Files:** `src/executor/l0_executor.py`
