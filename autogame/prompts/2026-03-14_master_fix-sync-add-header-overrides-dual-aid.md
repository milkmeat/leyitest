# Prompt Record

- Date: 2026-03-14 00:30
- Branch: master
- Commit: fix data sync: add header_overrides to game_api, dual-aid map brief for enemy discovery

---

### 1. Fix player data showing all zeros

先解决 1. 我看到现在我方玩家数据都还是0，可以连接test server先取到数据
城(0,0) 战力=0 兵力=0 出征槽位=2

> **Insight**
> **问题根源**：`cmd_config.yaml` 的 `get_player_info` 只配了 `svr_player` 一个模块，缺少 `svr_lord_info_new`/`svr_soldier`/`svr_hero_list`/`svr_buff`，导致同步时拿不到坐标、兵力、英雄等关键信息。

**Files:** `src/config/cmd_config.yaml`

### 2. Investigate enemy data missing from map brief

我确定敌方账号也在地图上。可能这个接口只返回同联盟信息，可以试一下用敌方uid查询。

> **Insight**
> 地图 brief API 按请求 header 中的 `aid` 过滤，只返回同联盟成员。用敌方 `aid=20000119` 查询时返回 21 个敌方玩家（含 2 个未知联盟成员），比逐个查询还多发现了额外敌人。

**Files:** `src/executor/game_api.py`, `src/models/enemy.py`, `src/perception/data_sync.py`

### 3. Test map brief with no uid/aid

试一下 查地图 brief 接口，如果不传uid/aid 是会报错，还是返回所有地图信息

> **Insight**
> - `aid=我方联盟` → 仅我方联盟成员（20人）
> - `aid=敌方联盟` → 仅敌方联盟成员（21人）
> - `aid=0` + 合法uid → 仅该 uid 自己（1人）
> - `aid=0, uid=0` → 无玩家（0人）
> 建筑始终全部返回，不受 aid 过滤。无法一次获取所有联盟玩家。

### 4. Use dual-aid approach instead of per-account query

> **Q:** 有两个方向：1. 补充敌方数据源（逐个查询）2. 用双 aid 地图 brief（2次请求）

用方案1. 并修改api接口使其支持override

**Files:** `src/executor/game_api.py`, `src/perception/data_sync.py`

### 5. Document map brief API behavior

把 查地图 brief api的用法记录到文档

**Files:** `docs/cmd_protocol_guide.md`
