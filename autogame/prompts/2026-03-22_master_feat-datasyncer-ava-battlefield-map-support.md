# Prompt Record

- Date: 2026-03-22 22:41
- Branch: master
- Commit: feat: DataSyncer AVA 战场地图支持

---

### 1. 实现 AVA 战场地图支持计划

Implement the following plan:

# Plan: DataSyncer AVA 战场地图支持

## Context

当前 `DataSyncer` 只用 `get_map_overview` (普通地图 API) 获取建筑和敌方数据，返回的是普通地图对象 (type=2 玩家, type=27/48/64/156 建筑)。当账号在 AVA 战场时，需要用 `lvl_battle_login_get` 获取战场地图，它返回不同的类型体系 (type=10101 城市, type=10000-10006 据点/建筑, type=10300 资源点)。

导致 L1 看不到目标建筑 pos:(154,170)，因为该建筑只存在于 AVA 地图中。

## 改动范围

### 1. `src/perception/data_sync.py` — 核心改动

**新增 AVA 类型常量:**
```python
AVA_PLAYER_TYPE = 10101
AVA_BUILDING_TYPES = {10000, 10001, 10002, 10006, 10103, 10104}
AVA_RESOURCE_TYPES = {10300}
```

**新增 `_sync_map_ava(uid, lvl_id)` 方法:**
- 调用 `self.client.lvl_battle_login_get(uid, lvl_id)`
- 解析 `svr_lvl_brief_objs` 中的 `briefObjs` 数组（注意：AVA 用 `briefObjs` 不是 `briefList`）
- AVA 对象是**扁平结构**（无 `objBasic` 嵌套），字段直接在顶层：`type, id, pos, camp, uniqueId, ...`
- type=10101 → Enemy（排除我方 uid）
- type in AVA_BUILDING_TYPES → Building
- type=10300 → 暂时忽略（资源点对战术决策价值低）

**修改 `_do_sync()` 方法:**
- 新增 `lvl_id` 参数（默认 0）
- `lvl_id != 0` 时调用 `_sync_map_ava()`，否则走原逻辑 `_sync_map_both_sides()`

**修改 `sync()` 方法:**
- 新增 `lvl_id` 参数透传

### 2. `src/models/building.py` — 兼容 AVA 扁平格式

**修改 `Building.from_brief_obj()`:**
- 当前已有 `basic = obj.get("objBasic", obj)` 回退逻辑，扁平结构会直接用 `obj` 自身
- 需要处理 AVA 特有字段：`camp` (替代 `aid`)、`uniqueId` (替代 `id` 格式)
- `unique_id` 解析：AVA 格式如 `10006_1773137411102403`，直接用 `uniqueId` 字段

### 3. `src/main.py` — CLI 参数

**给 `l1_decide`、`l1_view`、`sync`、`run` 命令加 `--ava <lvl_id>` 参数:**
- 传递到 DataSyncer.sync(lvl_id=xxx)
- `run` 命令已有透传机制，加一个参数即可

### 4. `src/controller/loop.py` — 主循环透传

**修改 `AIController.__init__` 和 `_run_one_loop`:**
- 新增 `lvl_id` 属性
- sync 阶段传入 `lvl_id`

> **Insight**
> - AVA 战场地图 API (`lvl_battle_login_get`) 返回的数据结构与普通地图 (`get_map_overview`) 完全不同：数据在 `svr_lvl_brief_objs.briefObjs` 中（注意不是 `briefList`），对象是**扁平结构**（字段直接在顶层，无 `objBasic` 嵌套）
> - 类型体系也不同：普通地图用 type=2/27/48/64/156，AVA 用 type=10101 (玩家城市)、10000-10006 (建筑据点)
> - 设计选择：`lvl_id != 0` 时走 AVA 分支，`lvl_id == 0` 走原有逻辑，保持向后兼容
> - **数据层兼容性设计**：`Building.from_brief_obj` 和 `Enemy.from_brief_obj` 使用 `obj.get("objBasic", obj)` 的回退模式——普通地图有 `objBasic` 则用之，AVA 扁平结构无此字段则回退到 `obj` 自身，一套代码兼容两种格式
> - **字段回退链**：`alliance_id = int(basic.get("aid", 0)) or int(basic.get("camp", 0))` — 先尝试普通地图的 `aid`，为 0 时再尝试 AVA 的 `camp`，利用 `or` 短路特性实现优雅回退

**Files:** `src/perception/data_sync.py`, `src/models/building.py`, `src/models/enemy.py`, `src/controller/loop.py`, `src/main.py`

### 2. 无 AVA 参数 L1 决策测试

python src/main.py --verbose l1_decide 1 --mock-l2 "[小队 1 (Alpha)] 控制 建筑 pos:( 154, 170 )" --l1-prompt ava

**Files:** (no file changes, validation run)

### 3. 确认带 AVA 参数运行

> **Q:** 要我带 `--ava 29999` 跑一次吗？

yes

> **Insight**
> - **之前（无 `--ava`）**：95 个普通地图建筑，找不到 (154,170)，L1 只能盲目移城
> - **现在（`--ava 29999`）**：11 个 AVA 建筑，目标 `10006_1773137411102403` at (154,170) 清晰可见
> - 调试中发现两个 plan 未预见的问题：(1) AVA 数据在 `push_list[2]` 而非 `[0]`；(2) AVA 玩家的 `uid` 字段为 0，实际 UID 在 `id` 字段

**Files:** `src/perception/data_sync.py`, `src/models/enemy.py`
