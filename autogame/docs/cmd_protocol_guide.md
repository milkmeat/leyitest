# 命令字协议用法指南

> 基于 `cmd_config.yaml` 定义 + test server 实际验证（2026-03-13）
> 调用方式：`GameAPIClient.send_cmd(cmd_name, uid, **overrides)`

## 坐标编码

后台统一使用整数坐标：`pos = x * 100_000_000 + y * 100`

```
示例: (123, 234) → 12300023400
示例: (724, 960) → 72400096000
解码: pos // 100_000_000 = x,  (pos % 100_000_000) // 100 = y
```

工具函数：`src/utils/coords.py` 的 `encode_pos(x, y)` / `decode_pos(pos)`

---

## 一、感知查询命令

### 1.1 get_all_player_data — 单玩家全量数据

| 项目 | 值 |
|------|------|
| 后台 cmd | `game_server_login_get` |
| 服务 | game_server |
| 作用域 | **仅返回 header.uid 指定的那个玩家自己的数据** |
| 参数 | `all: 1` |

**返回的数据模块：**

| 模块名 | 内容 | 团战用途 |
|--------|------|---------|
| `svr_user_objs` | 城市对象(type=2)：战力force、城墙wallInfo、增援reinforceInfo；NPC对象(type=71) | 获取自己的战力、城墙状态、增援槽位 |
| `svr_auto_user_rally_info` | 集结模式设置 | — |
| `svr_kingdom_info` | 王国信息、国王列表 | — |
| `svr_map_version` | 地图版本号 | 判断地图是否有更新 |
| `svr_player_gs_info` | 集结次数刷新时间 | — |
| `svr_warning_list` | 预警列表 | — |

**svr_user_objs 关键字段（type=2 城市对象）：**
```json
{
  "objBasic": {
    "type": 2,
    "id": "20001946",        // uid
    "pos": "12300023400"     // 编码坐标
  },
  "cityInfo": {
    "uname": "Boss_BWPLM",
    "level": 7,              // 城堡等级
    "force": "10087455",     // 战力（字符串）
    "reinforceSize": 5,      // 增援槽位上限
    "reinforcedNum": 1,      // 当前已增援数
    "wallInfo": {
      "durability": 1,       // 当前城墙耐久
      "maxDurability": 1     // 城墙最大耐久
    },
    "mainTroopUniqueId": "108_1772608072809832_1"  // 主力部队ID
  }
}
```

> **重要：此命令不能获取地图上其他玩家信息。** 要获取全图玩家，用 `get_map_overview`。

---

### 1.2 get_player_info — 分模块查询玩家数据

| 项目 | 值 |
|------|------|
| 后台 cmd | `login_get` |
| 服务 | ds_player |
| 作用域 | header.uid 指定的玩家，可查自己也可查别人 |
| 参数 | `all: 0, list: [模块名列表]`（`all:1` 返回全部模块） |

**可用模块：**

#### svr_lord_info_new — 领主基础信息
```json
{
  "lord_info_data": {
    "lord_info": {
      "uid": 20001946,
      "uname": "Boss_BWPLM",    // 玩家名
      "city_pos": 12300023400,   // 城市坐标
      "city_level": 7,           // 城堡等级
      "ksid": 1,                 // 王国ID
      "aid": 0,                  // 联盟ID（0=无联盟）
      "al_name": "",             // 联盟名
      "al_nick": ""              // 联盟缩写
    }
  }
}
```
用途：轻量坐标查询（get_player_pos 命令就是查这个模块）

#### svr_soldier — 士兵列表
```json
{
  "list": [
    {"id": 101, "value": 0},       // 射手(archer)
    {"id": 201, "value": 0},       // 步兵(infantry)
    {"id": 204, "value": 2000000}, // 骑兵(cavalry)
    {"id": 1,   "value": 19}       // 其他类型
  ]
}
```
用途：获取城内兵种数量，用于决定派兵组成

#### svr_hero_list — 英雄列表
```json
{
  "heros": [
    {
      "id": 21,               // 英雄ID
      "lv": 7,                // 等级
      "state": 0,             // 0=空闲可用，其他=出征中
      "skill_lv": [1, 0, 0],  // 技能等级
      "slg_skill_lv": [1, 0]  // SLG 技能等级
    }
  ]
}
```
用途：查看可用英雄，`state=0` 才能带兵出征

#### svr_buff — Buff 列表
```json
{
  "buff_item": [
    {"id": 1001, "buff_num": 3}
  ]
}
```

#### svr_player — 玩家基础信息
包含联盟等基础属性。

---

### 1.3 get_map_overview — 地图全局概览

| 项目 | 值 |
|------|------|
| 后台 cmd | `get_map_brief_obj` |
| 作用域 | 地图所有建筑/NPC + **header.aid 所属联盟的玩家城市** |
| 参数 | `sid: 1`（必须传 sid=1，sid=0 可能返回不同结果） |
| header 关键字段 | `aid` — 决定返回哪个联盟的玩家（见下方行为说明） |

#### header.aid 对 type=2 玩家返回的影响（实测 2026-03-14）

| header.aid | header.uid | type=2 返回 | 建筑等非玩家对象 |
|------------|-----------|-------------|-----------------|
| 我方联盟 aid (20000118) | 任意 | **仅我方联盟成员**（20人） | 全部返回（118个） |
| 敌方联盟 aid (20000119) | 敌方uid | **仅敌方联盟成员**（21人） | 全部返回（118个） |
| 0 | 合法uid | **仅该 uid 自己**（1人） | 全部返回（118个） |
| 0 | 0 | **无玩家**（0人） | 全部返回（118个） |

> **关键发现：服务器按 `header.aid` 过滤 type=2 玩家，只返回同联盟成员。**
> 建筑（type=8/27/48/64/121/156）不受 aid 过滤，始终全部返回。
> 不存在"一次返回所有联盟玩家"的方式。

**当前 data_sync 策略：** 分别用我方 aid 和敌方 aid 各请求一次（共 2 次），合并结果。
代码：`DataSyncer._sync_map_both_sides()` — 并发 2 次请求，建筑从我方响应取，敌方玩家从敌方响应取。

```python
# 用法示例：用敌方 aid 查询敌方联盟成员位置
resp = await client.get_map_overview(
    enemy_uid, sid=1,
    header_overrides={"aid": enemy_aid},
)
```

**返回的数据模块：**

#### svr_map_brief_objs — 地图简要对象列表

test server 实测返回 ~138 个对象（取决于 aid），type 分布：

| type | 含义 | 数量(示例) | 受 aid 过滤 | 关键字段 |
|------|------|-----------|:-----------:|---------|
| 2 | 玩家城市 | 20-21 | **是** | uid, pos, aid, ksid, fightFlag |
| 8 | 联盟建筑/堡垒 | 18 | 否 | aid, alName, alNick, alFlag, key |
| 27 | 据点/资源点 | 74 | 否 | pos, key |
| 64 | 城市据点 | 16 | 否 | pos, key |
| 121 | 高级要塞 | 5 | 否 | aid, alName |
| 156 | KVK 据点 | 4 | 否 | — |
| 48 | KVK 城堡 | 1 | 否 | — |

**type=2 玩家城市对象示例：**
```json
{
  "uniqueId": "2_20010643_1",
  "objBasic": {
    "type": 2,
    "pos": "36500063000",    // 编码坐标
    "sid": 1,
    "uid": "20010643",       // 玩家 UID
    "aid": "20000118",       // 联盟 ID
    "ksid": "1",
    "fightFlag": 0           // 战斗标志
  }
}
```

> **注意：此命令只返回坐标和联盟信息，不包含战力、兵种等详细数据。** 详细数据需对每个 uid 单独调 `get_all_player_data` 或 `get_player_info`。

#### svr_mini_al_building_list — 联盟小型建筑列表
```json
{
  "list": [
    {
      "pos": "32700091700",
      "territorySize": 15,
      "aid": "20000050",
      "alFlag": 7,
      "type": 8
    }
  ]
}
```

---

### 1.4 get_map_detail — 地图区块详情

| 项目 | 值 |
|------|------|
| 后台 cmd | `game_svr_map_get` |
| 参数 | `sid: 1, bid_list: [区块ID列表]` |
| 返回模块 | `svr_map_objs_new` |

> 注意：`bid_list` 为空时返回空对象。需传入具体区块 ID 才能获取详情。

---

### 1.5 get_al_members — 联盟成员列表

| 项目 | 值 |
|------|------|
| 后台 cmd | `get_self_al_member` |
| 参数 | 无（需 header 中有正确的 aid） |

---

### 1.6 get_battle_report — 战报查询

| 项目 | 值 |
|------|------|
| 后台 cmd | `get_city_battle_report` |
| 参数 | `id: "报告ID"` |

---

## 二、行动指令

### 2.1 move_city — 定点移城

| 项目 | 值 |
|------|------|
| 后台 cmd | `fixed_move_city_new` |
| 参数 | `use_gem: 1, item_id: 1, tar_pos: 编码坐标` |
| 效果 | 瞬间传送主城 + 自动召回所有在外部队 |

```python
await client.send_cmd("move_city", uid, tar_pos=encode_pos(500, 500))
```

> **移城是最强战术操作**：无 CD，瞬移 + 全军秒回 + 重新部署。

---

### 2.2 attack_player — 攻击玩家主城

| 项目 | 值 |
|------|------|
| 后台 cmd | `dispatch_troop` |
| 参数 | `march_type: 2, target_type: 2, target_info: {id, pos}, march_info: {soldier, hero}` |

```python
await client.send_cmd("attack_player", uid,
    target_info={"id": "2_20010643_1", "pos": str(encode_pos(365, 630))},
    march_info={"soldier": {"204": 50000}, "hero": {"main": 21}}
)
```

---

### 2.3 attack_building — 攻击建筑/据点

| 项目 | 值 |
|------|------|
| 后台 cmd | `dispatch_troop` |
| 参数 | `march_type: 2, target_type: 13, target_info: {id, pos}, march_info: {soldier, hero}` |

---

### 2.4 reinforce_building — 增援/驻防建筑

| 项目 | 值 |
|------|------|
| 后台 cmd | `dispatch_troop` |
| 参数 | `march_type: 11, target_info: {id, pos}, march_info: {soldier, hero}` |

---

### 2.5 scout_player — 侦察

| 项目 | 值 |
|------|------|
| 后台 cmd | `dispatch_scout` |
| 参数 | `scout_queue_id: 8001, tar_type: 5, tar_pos: 编码坐标, need_camp: 0` |

---

### 2.6 create_rally — 发起集结

| 项目 | 值 |
|------|------|
| 后台 cmd | `create_rally_war` |
| 参数 | `march_type: 13, target_type: 2, target_info: {id}, tn_limit: 1, march_info: {队长部队}, prepare_time: 300` |

```python
await client.send_cmd("create_rally", uid,
    target_info={"id": "2_20010643_1"},
    march_info={"soldier": {"204": 50000}, "hero": {"main": 21}},
    prepare_time=300,
    timestamp=str(int(time.time() * 1000000))  # 微秒时间戳
)
```

---

### 2.7 join_rally — 加入集结

| 项目 | 值 |
|------|------|
| 后台 cmd | `dispatch_troop` |
| 参数 | `march_type: 12, target_type: 107, target_info: {id: rally_unique_id, pos}, march_info: {}` |

> **注意**：`march_type=12`（非13），`target_type=107`（非2），target_info.id 是 rally 的 unique_id（107_xxx_1 格式）。

---

### 2.8 rally_dismiss — 解散集结（队长操作）

| 项目 | 值 |
|------|------|
| 后台 cmd | `rally_dismiss` |
| 参数 | `unique_id: "107_xxx_1"` |

---

### 2.9 recall_reinforce — 召回增援部队（队员操作）

| 项目 | 值 |
|------|------|
| 后台 cmd | `recall_reinforce` |
| 参数 | `unique_id: "101_xxx_1"`（本人部队的 unique_id） |

---

### 2.10 recall_troop — 召回行军部队

| 项目 | 值 |
|------|------|
| 后台 cmd | `change_troop` |
| 参数 | `march_type: 5, march_info: {"ids": [部队unique_id]}` |

---

## 三、数据感知查询模式

团战 AI 获取全局态势的标准流程：

```
Step 1: get_map_overview × 2（并发，共 2 次请求）
   ├─ aid=我方 → 我方玩家 uid+坐标 + 全部建筑/据点
   └─ aid=敌方 → 敌方玩家 uid+坐标（建筑重复，忽略）

Step 2: 对每个我方 uid，并发调用 get_player_info：
   → 士兵数量、英雄状态、buff

Step 3（可选）: 对需要详查的 uid，调用：
   └─ get_all_player_data(uid)  → 战力、城墙、增援信息
```

> **注意**：Step 1 必须分两次请求（我方 aid + 敌方 aid），
> 因为地图 brief API 按 header.aid 过滤 type=2 玩家，无法一次获取所有联盟。
> 详见 1.3 节的 aid 过滤行为表。

**信息分布在两个后端服务上：**

| 信息 | 服务 | 命令 |
|------|------|------|
| 地图全局对象 | game_server | `get_map_brief_obj` |
| 战力、城墙、行军 | game_server | `game_server_login_get` |
| 士兵数量、英雄、buff | ds_player | `login_get` |

---

## 四、GM / 准备阶段命令

| cmd_name | 后台 cmd | 用途 |
|----------|---------|------|
| `add_gem` | `op_self_set_gem` | 添加宝石 |
| `add_soldiers` | `op_add_soldiers` | 添加士兵（soldier_id + soldier_num） |
| `add_resource` | `op_self_add_clear_resource` | 添加资源 |
| `copy_player` | `op_copy_player` | 复制账号数据 |
| `change_name` | `player_name_change` | 改昵称 |

## 五、联盟操作命令

| cmd_name | 后台 cmd | 用途 |
|----------|---------|------|
| `create_alliance` | `al_create` | 创建联盟（name 5-20字符, nick 3-4字符） |
| `join_alliance` | `al_request_join` | 申请加入联盟 |
| `al_leave` | `al_leave` | 离开联盟 |
| `al_help_all` | `al_help_all` | 一键帮助盟友 |

## 六、AVA 战场命令

| cmd_name | 后台 cmd | 用途 |
|----------|---------|------|
| `create_ava_battle` | `op_create_lvl_battle` | 创建 AVA 临时战场 |
| `ava_add_player` | `op_lvl_set_player` | 添加玩家到战场 |
| `ava_enter_battle` | `op_enter_lvl_battle` | 进入战场 |
