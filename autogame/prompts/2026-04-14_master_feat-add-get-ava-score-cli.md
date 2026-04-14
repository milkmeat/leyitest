# Prompt Record

- Date: 2026-04-14 10:00
- Branch: master
- Commit: feat: 新增 get_ava_score CLI 命令（AVA 战场积分总览）

---

### 1. 探测 get_battle_server_detail 命令

ava 战场有一个 get_battle_server_detail 命令，在test环境上探测一下它的返回内容，保存到docs/samples

> **Insight**
> - `get_battle_server_detail`（无 lvl_ 前缀）走 `battle_type/battle_id` 路由，测试服代理不支持，始终返回 30112 data_key 路由失败
> - 加 `lvl_` 前缀后走 `lvl_id` 路由就通了，和其他 AVA 命令命名规律一致
> - 返回的数据模块是 `svr_lvl_war_situation_detail`，包含双方阵营所有成员的实时积分排行
> - `scoreSpeed` 字段表示当前积分增长速率（每分钟），非零说明该玩家正在进行产分行为

**Files:** `docs/samples/get_battle_server_detail__FAILED__20010643.json`, `docs/samples/lvl_get_battle_server_detail__20010643.json`

### 2. 记录 AVA 命令需要已入场 UID

记录一下，在test env上使用ava相关的命令时，需要使用一个已经加入到ava战场的uid

### 3. 添加 lvl_get_battle_server_detail 到 CLI

先把 lvl_get_battle_server_detail 命令字添加到cli，更新 yaml文件，api接口， cli 命令

**Files:** `docs/references/cmd_config.yaml`, `src/config/cmd_config.yaml`, `src/executor/game_api.py`, `src/main.py`

### 4. 测试 lvl_battle_login_get 的 svr_lvl_war_situation

测试一下 lvl_battle_login_get 命令字，读取 svr_lvl_war_situation 中的信息

> **Insight**
> - `svr_lvl_war_situation`（来自 `lvl_battle_login_get`）是阵营级汇总：总分、建筑占领、积分速率、参战人数
> - `svr_lvl_war_situation_detail`（来自 `lvl_get_battle_server_detail`）是个人级明细：每个成员的 score/rank/scoreSpeed
> - 两者互补：前者看全局态势，后者看个人贡献

### 5. 合并为 get_ava_score 命令

去掉 cli命令 lvl_get_battle_server_detail，更新成 get_ava_score, 同时返回 svr_lvl_war_situation与 svr_lvl_war_situation_detail 的信息

**Files:** `src/main.py`

### 6. 修正 scoreSpeed 单位

个人得分speed 是分钟为单位的，是120/min, 不是 120/s ， 联盟得分单位也是 5520/min

**Files:** `src/main.py`, `src/executor/game_api.py`

### 7. 更新 --help 信息

--help 所打印的message也更新一下

**Files:** `src/main.py`
