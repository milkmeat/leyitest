# Prompt Record

- Date: 2026-04-09 00:00
- Branch: master
- Commit: feat: 新增批量采集 AVA 战场所有 coal cart 脚本

---

### 1. 批量采集 coal cart 脚本

写一个脚本，让20010643采集ava战场里面所有的coal cart

> **Insight**
> - 现有代码只采集最近的 1 个 cart，因为采集队列 `queue_id=6003` 只有一个槽位
> - 要采集"所有" cart，需要循环：查地图 → 采最近的 → 等采集完成 → 再查再采
> - 通过轮询 `lvl_battle_login_get` 检查 march_type=21 的部队状态来判断采集是否完成
> - 采集队列 `queue_id=6003` 是独立于战斗出征队列（6001/6002）的，所以采集不会占用攻击槽位
> - `march_type=21` 是采集专用行军类型，`lvl_dispatch_pick` 命令不需要指定兵力信息，服务器自动处理
> - 脚本通过轮询 `svr_lvl_brief_objs` 中 type=101（行军队伍）的 marchType 字段来判断采集是否完成

**Files:** `scripts/collect_all_carts.py`
