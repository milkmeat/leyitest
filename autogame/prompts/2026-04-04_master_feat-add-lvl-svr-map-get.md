# Prompt Record

- Date: 2026-04-04
- Branch: master
- Commit: feat: 集成 lvl_svr_map_get 战场地块详情查询 API（含 bid 计算、CLI 命令、DataSyncer 支持）

---

### 1. Merge lvl_svr_map_get from game_actions.py reference

docs/references/cmd_config.yaml (game_actions.py) 下面有一个 lvl_svr_map_get 命令字的实现，将其合并到我们的项目中

> **Insight**
> - `lvl_battle_login_get` 返回 `svr_lvl_brief_objs`（全战场的概要对象列表，扁平结构）
> - `lvl_svr_map_get` 返回 `svr_lvl_map_objs.mapBidObjs`（按地块 bid 分组的详细对象，含城市等级/兵力/camp、建筑驻军、行军类型等）
> - 两者互补：brief 用于全局扫描，detail 用于局部精确查询（如驻军数、玩家兵力）

**Files:** `src/utils/coords.py`, `src/config/cmd_config.yaml`, `src/executor/game_api.py`, `src/perception/data_sync.py`

### 2. Ask how to test lvl_svr_map_get via CLI

使用什么cli命令可以测试lvl_svr_map_get

> **Insight**
> - 参数: `<uid> <lvl_id> <center_x> <center_y> [size]` — uid 是查询用的账号（需在战场内），size 默认 10（即 10x10=100 个 bid 地块）
> - bid 计算: 自动将像素坐标 (154, 170) 转为地块 bid=(16, 18)，size=10 则查询 bx=[11..20], by=[13..22] 共 100 个 bid
> - 输出格式: 逐地块打印玩家城（等级/兵力/camp）、建筑（驻军数）、行军队伍（marchType），空地块跳过

**Files:** `src/main.py`
