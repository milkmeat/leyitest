# Prompt Record

- Date: 2026-04-07 17:30
- Branch: master
- Commit: feat: 新增 collect_cart CLI 命令，AVA 战场搜集最近 coal cart (lvl_dispatch_pick)

---

### 1. 新增 collect_cart CLI 命令

增加一个cli 命令, "collect_cart <uid> --ava 29999", 则该玩家会派出一个行军队列搜集地图上最近的一个coal cart(10300)

> **Insight**
> AVA 战场中的 coal cart (type=10300) 本质上是资源点。采集它需要用 `lvl_dispatch_troop`，但 march_type 要设为 4（采集资源地），而非 2（攻击）或 15（攻打建筑）。这和普通地图的 `dispatch_collect_troop` 不同 — AVA 战场内所有行军操作都走 `lvl_dispatch_troop` 这个统一入口，通过 march_type 区分行为。

**Files:** `src/config/cmd_config.yaml`, `src/executor/game_api.py`, `src/main.py`

### 2. 提供正确的命令字 lvl_dispatch_pick

搜集矿车用的是一个新命令字，请实现：

--
04-07 17:52:29.945 W/Unity   ( 4476): [MdNetParam ToUrl]:lvl_dispatch_pick:1155:399.4837
04-07 17:52:29.945 W/Unity   ( 4476): {"param":{"march_type":21,"unique_id":"","target_info":{"type":10300,"id":"10300_1775212335695081"},"queue_id":6001}}
04-07 17:52:29.945 W/Unity   ( 4476): UnityEngine.Logger:Log(LogType, Object)
04-07 17:52:29.945 W/Unity   ( 4476): NetReq:ToRequestJson(JSONObject)

> **Insight**
> `lvl_dispatch_pick` 是 AVA 战场专用的"拾取"命令字，和 `lvl_dispatch_troop`（派兵）是完全独立的。它不需要 `march_info`（兵力/英雄配置），服务器会自动分配一个搜集队列去拾取目标资源车。`march_type=21` 是 pick 专用类型。

**Files:** `src/config/cmd_config.yaml`, `src/executor/game_api.py`, `src/main.py`
