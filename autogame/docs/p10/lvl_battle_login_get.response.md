# lvl_battle_login_get 响应结构分析

> 命令字: `lvl_battle_login_get`
> 测试账号: UID 20010643, lvl_id=29999
> 采样时间: 2026-04-07
> 原始响应: `docs/samples/lvl_battle_login_get__20010643.json` (411 KB)

## 返回的 data section 总览

| Section | 内容 | 数据量 | CLI 关键词匹配 |
|---------|------|--------|---------------|
| `svr_lvl_brief_objs` | 地图全量对象（玩家城、建筑、资源点） | 2148 个对象 | objs ✓ |
| `svr_lvl_joiner_info` | 两个阵营的成员信息 | 2 items | — |
| `svr_lvl_mercenary_building_button` | 佣兵建筑按钮状态 | 1 item | — |
| `svr_lvl_rally_brief_objs` | 当前活跃的集结概览（含行军路径、目标、参与者） | 3 个集结 | rally ✓ |
| `svr_lvl_side_buff` | 双方阵营 buff | 2 items | — |
| `svr_lvl_user_info` | 当前玩家移城信息（次数、冷却） | 单对象 | — |
| `svr_lvl_user_objs` | 当前玩家的详细部队对象（含兵种、行军、战斗状态） | 3 个对象 | objs ✓ |
| `svr_lvl_version` | 战场版本号 | 单值 | — |
| `svr_lvl_war_situation` | 战况（阵营得分、建筑占领数、地图ID） | 单对象 | — |
| `svr_lvl_warning_list` | 警告列表 | 空 | — |

---

## 1. svr_lvl_brief_objs — 地图全量对象

### 对象类型分布

| type | 含义 | 数量 | 占比 |
|------|------|------|------|
| 10101 | 玩家城 | 22 | 1.0% |
| 10000 | 纪念碑 (Monument) | 2 | 0.1% |
| 10001 | 要塞 (Fortress) | 5 | 0.2% |
| 10002 | 哨塔 (Watchtower) | 2 | 0.1% |
| 10006 | 堡垒 (Bastion) | 1 | <0.1% |
| 10103 | 兵营 (Barracks) | 1 | <0.1% |
| 10104 | 医院 (Hospital) | 1 | <0.1% |
| 10300 | 资源点 | 2117 | 98.6% |

### 玩家城 (type=10101)

```json
{
  "uniqueId": "10101_20010643",
  "type": 10101,
  "id": "20010643",           // UID（注意是字符串）
  "pos": "400000000",         // 编码坐标
  "camp": "1",                // 阵营 1=我方, 2=敌方
  "openTime": "0",
  "occupying": 0,
  "occupyingEtime": "0",
  "num": 1,                   // 城内部队数
  "key": "965",               // 地图 key
  "fightFlag": 0,             // 是否在战斗
  "castleLevel": 30,          // 城堡等级
  "limitTroopNum": 800000,    // 兵力上限
  "curTroopNum": 0,           // 当前驻防兵力（自己的城显示0，敌方可见）
  "troopUniqueIds": [         // 关联部队 ID
    "108_1775212335679755"
  ],
  "comingFightNum": 0,        // 正在来攻的敌军数量
  "arriveNum": 1,             // 已到达的部队数
  "lordName": "p10-test-20010643",
  "reinforceSize": 5,         // 援军槽位上限
  "reinforcedNum": 1          // 已驻防援军数
}
```

可选字段（部分玩家城有）:
- `aimedInfos`: `[{"camp": 1, "num": 1}]` — 被瞄准信息（哪个阵营、几支部队正在朝这里来）

### 建筑通用结构 (type=10000/10001/10002/10006/10103/10104)

```json
{
  "uniqueId": "10001_1773137411102402",
  "type": 10001,
  "id": "1773137411102402",   // 建筑实例 ID
  "pos": "10100018300",       // 编码坐标
  "camp": "1",                // 当前归属阵营
  "openTime": "1686809423000",// 开放时间（毫秒时间戳）
  "occupying": 0,             // 是否正在被占领
  "occupyingEtime": "0",      // 占领结束时间
  "num": 0,                   // 驻防部队数
  "key": "954",               // 地图 key
  "fightFlag": 0,             // 是否在战斗
  "mailDocIds": [...],        // 相关邮件 ID
  "castleLevel": 0,
  "limitTroopNum": 0,         // 兵力上限（无驻防时为0）
  "curTroopNum": 0,           // 当前驻防兵力
  "comingFightNum": 0,        // 来攻敌军数
  "oldCamp": 2,               // 原始归属阵营（用于判断是否被翻转）
  "arriveNum": 0,
  "reinforceSize": 5,
  "reinforcedNum": 0
}
```

有驻防时额外字段（如 10103/10104）:
- `troopUniqueIds`: 驻防部队 ID 列表
- `lordName`: 驻防者名称
- `aimedInfos`: 被瞄准信息

### 资源点 (type=10300) — 极简结构

```json
{
  "uniqueId": "10300_1773137411108025",
  "type": 10300,
  "id": "1773137411108025",
  "pos": "15600016400",
  "key": "1220001"            // 资源类型 key
}
```

---

## 2. svr_lvl_rally_brief_objs — 集结概览

每个集结对象:

```json
{
  "uniqueId": "107_1775212335694384",
  "type": 107,
  "id": "1775212335694384",
  "camp": 1,
  "targetId": "10001_1773137411102408",  // 目标 uniqueId
  "tarType": 10001,                       // 目标类型（要塞）
  "tarId": "1773137411102408",
  "tarCamp": 2,                           // 目标阵营
  "stime": "1775530050964",              // 集结发起时间（毫秒）
  "status": 1,                            // 1=行军中, 6=等待集合中
  "isAttack": 1,                          // 1=进攻集结
  "march": {
    "btime": "1775530110980",            // 行军开始时间
    "etime": "1775530605762",            // 行军预计到达时间
    "status": 1,
    "move": {
      "speed": 341,
      "paths": ["500000100", "10632013594"],  // 路径点（编码坐标）
      "pathIndex": 0
    },
    "marchType": 13                       // 13=集结行军
  },
  "pos": "9133011598",                   // 当前位置
  "seq": "15521236040268",
  "tarKey": 953,
  "tarName": "",
  "tarPos": "10600013600",               // 目标位置
  "ownerUid": "20010643",                // 发起者 UID
  "rallyFighting": 0,
  "showPower": 1,
  "leaderUid": "20010669",               // 队长 UID
  "initTarPos": "10600013600"            // 初始目标位置
}
```

---

## 3. svr_lvl_user_objs — 当前玩家详细部队

返回当前查询账号的所有对象（部队+城），结构比 briefObjs 详细得多，有 `objBasic` 嵌套。

### 单兵部队 (type=101)

```json
{
  "uniqueId": "101_1775212335694384",
  "objBasic": {
    "type": 101,
    "id": "1775212335694384",
    "pos": "400000000",
    "key": 0,
    "seq": "...",
    "uid": "20010643",
    "dir": "0",
    "curMs": "1775530537038",
    "camp": 1,
    "status": 8                // 部队状态
  },
  "marchBasic": {
    "btime": "0",
    "etime": "0",
    "status": 8,               // 8=驻扎
    "move": { "speed": 100 },
    "marchType": 12,           // 12=驻防行军类型
    "tpInfo": { "btime": "0", "ctime": "0" },
    "queueId": "6001",
    "ctime": "0"
  },
  "fightBasic": {
    "isFight": 0,
    "besiegeCount": 0,
    "originTroopNum": 5000,
    "rallyFighting": 0
  },
  "troopInfo": {
    "troop": [{ "id": 204, "num": 5000 }],   // 兵种ID + 数量
    "troopStatus": 1,
    "target": {                                // 当前目标
      "type": 107,
      "id": "1775212335694384",
      "uniqueId": "107_1775212335694384",
      "key": 0,
      "pos": "500000100",
      "uid": "20010643",
      "campId": "1"
    },
    "hurtTroop": [{ "id": 204, "num": 0 }],  // 伤兵
    "defendFightStatus": 0,
    "protectCoffin": 2,
    "curLoad": "0",
    "totalLoad": "80000000",
    "lord": {
      "lordSkinId": 0,
      "lordLevel": 1,
      "lordName": "p10-test-20010643",
      "lordState": 0
    },
    "uname": "p10-test-20010643",
    "queueId": 6001,
    "isMainTroop": 1,
    "from": {                                  // 出发地
      "type": 10101,
      "id": "20010643",
      "key": 965,
      "pos": "400000000"
    }
  }
}
```

### 集结队伍 (type=107)

在 `troopInfo` 基础上额外有 `rallyInfo`:

```json
{
  "rallyInfo": {
    "target": { "type": 10001, "id": "...", "pos": "10600013600", "campId": "2" },
    "limitTroopNum": 1851450,
    "curTroopNum": 10000,
    "stime": "1775530050",
    "mainDefendUniqueId": "101_1775212335694384",
    "troop": [{ "id": 204, "num": 10000 }],
    "targetReinforceInfo": {
      "limitTroopNum": 1851450,
      "curTroopNum": 10000,
      "reinforceSize": 5,
      "reinforcedNum": 2,
      "joinerInfos": [
        { "uid": "20010669", "uname": "p10-test-20010669", "startTime": "1775528750" },
        { "uid": "20010671", "uname": "p10-test-20010671", "startTime": "1775528752" }
      ],
      "leaderUid": "20010669"
    },
    "tnLimit": 15,                              // 集结人数上限
    "troopUniqueId": ["101_...", "101_..."],     // 参与部队
    "joinerInfos": [
      { "uid": "20010643", "startTime": "0" },
      { "uid": "20010648", "startTime": "1775530055" }
    ],
    "reinforceSize": 5,
    "reinforcedNum": 2,
    "initTarPos": "10600013600",
    "mainTroop": [{ "id": 204, "num": 5000 }]  // 队长主力兵种
  }
}
```

### 玩家城详情 (type=10101, user_objs 版)

比 briefObjs 多出 `cityInfo`:

```json
{
  "cityInfo": {
    "level": 30,
    "skin": 0,
    "force": "17130995",          // 战力
    "killNum": "859",             // 击杀数
    "smoking": 0,                 // 是否冒烟
    "burningEtime": "0",          // 燃烧结束时间
    "limitTroopNum": 800000,
    "curTroopNum": 0,
    "troop": [{ "id": 204, "num": -210000 }],  // 城内兵力（负数=已派出）
    "passiveMove": 0,
    "moveCityFlag": 0,
    "hasArrest": 0,
    "reinforceSize": 5,
    "reinforcedNum": 1,
    "wallInfo": {                 // 城墙信息
      "durability": 1200,
      "maxDurability": 1200,
      "fireCpuTime": "0",
      "fireEtime": "0",
      "fireBDurability": 0,
      "fireEDurability": 0
    },
    "mainTroopUniqueId": "108_1775212335679755"
  }
}
```

---

## 4. svr_lvl_user_info — 玩家移城信息

```json
{
  "moveTimes": 1,                 // 已移城次数
  "moveCoolEtime": "1775530576"   // 移城冷却结束时间（秒级时间戳）
}
```

---

## 5. svr_lvl_war_situation — 战况信息

```json
{
  "avaId": "29999",
  "avaStageInfo": { ... },        // 阶段信息（2 keys）
  "avaCampInfo": [ ... ],         // 双方阵营积分（2 items）
  "totalLandBuildingNum": 11,     // 地图建筑总数
  "mapId": 1,
  "monumentWarScaleCap": "0",
  "monumentWarScaleLv": "0"
}
```

---

## 注意事项

1. `svr_lvl_user_objs` 只返回**当前查询账号**的部队详情；要获取所有账号状态需逐个调用 `login_get`
2. `briefObjs` 中自己城的 `curTroopNum=0`，实际兵力在 `svr_lvl_user_objs.cityInfo` 中
3. 资源点 (10300) 占 98.6% 的对象，同步时应过滤以减少处理开销
4. AVA 对象是**扁平结构**（字段直接在顶层），而 `svr_lvl_user_objs` 使用 `objBasic` 嵌套结构
5. 玩家城的 `id` 字段即 UID（字符串类型），建筑的 `id` 是实例 ID
6. `camp` 字段为字符串 "1"/"2"，非整数
