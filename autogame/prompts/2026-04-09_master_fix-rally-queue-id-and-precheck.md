# Prompt Record

- Date: 2026-04-09 14:40
- Branch: master
- Commit: fix: 修复集结队列 queue_id 错误（JOIN_RALLY 改 6004）并添加 6002 占用预检查

---

### 1. 调查 rally 集结 30001 错误

看一下为什么以下rally集结失败，可以使用该小队在test环境重现一下
14:37:14 [src.executor.game_api] WARNING: [业务失败] cmd_name=lvl_create_rally_war cmd=lvl_create_rally_war uid=20010671 code=30001
Header: {"did": "self-system", "sid": 1, "aid": 20000118, "ksid": 1, "lvl_id": 29999, "castle_lv": 25, "battle_type": 0, "battle_id": 0, "chat_scene": ",kingdom_1", "invoker_name": "ying_test_debug", "uid": 20010671}
Param: {"march_info": {"hero": {"main": 416, "vice": []}, "carry_lord": 1, "leader": 1, "soldier_total_num": 5000, "heros": {}, "queue_id": 6002, "soldier": {"204": 5000}, "over_defend": false}, "march_type": 14, "prepare_time": 60, "recommand_troop": [], "target_info": {"id": "10000_1775557705871685"}, "target_type": 10000, "timestamp": "1775716633964752", "tn_limit": 15}
Response: {"res_header": {"ret_code": 30001, "cost_time_us": 0, "ret_time_s": 1775716634, "err_msg": ""}, ...}
14:37:14 [src.executor.l0_executor] WARNING: L0 服务器返回错误: LVL_INITIATE_RALLY_BUILDING uid=20010671 —  (Invalid operation. Please restart the game and try again.)

> **Insight**
> 根因: queue_id=6002 已被占用。服务器 err_msg 明确返回: `cmd_check_dispatch_ds.lua:97] this queueid=6002 has occupied`。每个玩家只有一个 6002 集结队列槽位，当已有活跃集结时再次发起就会 30001。

**Files:** `src/executor/l0_executor.py`, `src/config/cmd_config.yaml`

### 2. 确认集结队列 ID 分配

> **Q:** 要在 L0 executor 中添加 queue_id=6002 占用预检查吗？

发起集结使用6002，参加集结使用6004

**Files:** `src/executor/l0_executor.py`, `src/config/cmd_config.yaml`
