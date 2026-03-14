# Prompt Record

- Date: 2026-03-13 21:30
- Branch: master
- Commit: add cmd protocol guide with test server verified usage patterns

---

### 1. 验证 game_server_login_get 能否获取全图玩家信息

game_server_login_get 这个命令字能拿到地图上所有玩家的信息吗？在test server上验证一下

> **Insight**
> 1. **`game_server_login_get` 不能拿到地图上所有玩家信息。** svr_user_objs 仅包含 1 个对象（自己的城市，type=2）。它的价值是获取该玩家的详细信息：战力 force、城墙 wallInfo、增援 reinforceInfo、行军队列等。
> 2. **`get_map_brief_obj` (get_map_overview)** 才是获取地图上所有对象的命令。test server 上返回了 138 个对象，其中 type=2 玩家城市 20 个。
> 3. **数据互补关系**：get_map_overview 只给概览（uid、坐标、联盟），没有战力、兵种等详细信息。要拿详细数据，需要对每个 uid 分别调 game_server_login_get 或 login_get。这就是数据感知层的两步查询模式。

### 2. 记录协议命令字用法到文档

把这些协议命令字的用法记录到文档

> **Insight**
> 1. **两服务架构**是理解这套协议的关键：game_server 管地图对象和战力，ds_player 管玩家属性（兵种/英雄/buff）。同一个玩家的完整数据散落在两个服务上，这就是为什么感知层需要"两步查询"模式。
> 2. **uniqueId 的命名规则**暗藏对象类型：2_xxx_1 是玩家城市，107_xxx_1 是集结对象，101_xxx_1 是增援部队，108_xxx_1 是主力部队。前缀数字就是 type 值。
> 3. 文档按 感知 → 行动 → 准备 的逻辑组织，与 AI 主循环的 Phase 顺序（Sync → L2/L1 → Action）对应。

**Files:** `docs/cmd_protocol_guide.md`
