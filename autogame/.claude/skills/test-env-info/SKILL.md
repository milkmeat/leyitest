---
name: test-env-info
description: Display information about the WestGame test environment and AVA battlefield system. Use when user asks about environment configuration, server URLs, account distribution, or AVA battlefield status.
license: MIT
---

# WestGame 环境信息

## Test 测试环境配置

**位置**: `config/env_config.yaml`

```yaml
current_env: test

environments:
  test:
    name: "测试环境"
    url: "https://leyi-offline-game-alb.leyinetwork.com/p10-test-lc-proxy"

  mock:
    name: "本地Mock"
    url: "http://localhost:18888/mock"
```

### 关键配置参数 (default_header)

| 参数 | 值 | 说明 |
|------|-----|------|
| `did` | "self-system" | 设备ID |
| `sid` | 1 | 场景ID（1=活动地图） |
| `aid` | 20000118 | 联盟ID (TestSquad2026，我方) |
| `ksid` | 1 | 场景key |
| `ava_id` | 0 | AVA战场ID（0=普通地图，非0=战场副本ID） |
| `castle_lv` | 25 | 城堡等级 |
| `battle_type` | 0 | 战斗类型 |
| `battle_id` | 0 | 战斗ID |
| `chat_scene` | ",kingdom_1" | 聊天场景 |
| `invoker_name` | "evans_test_debug" | 调用者标识 |

### 请求附加信息 (extra_info)

```yaml
extra_info:
  no_checkac: 1
  op_cmd: 1
```

---

## AVA 战场系统

### 检测账号是否在AVA战场

使用 `GameAPIClient.get_player_lvl_info(uid)` 方法：

```python
# 返回值
lvl_id = await api.get_player_lvl_info(uid)
# lvl_id = 0 → 在普通地图
# lvl_id != 0 → 在AVA战场副本（值为战场ID）
```

**实现原理**：调用 `get_player_lvl_info` 命令字，解析响应中的 `svr_player_lvl_info` 模块的 `lvl_id` 字段。

**检查脚本**: `python scripts/check_ava_accounts.py`

### AVA战场专用命令字

AVA战场内的命令字使用 `lvl_` 前缀，与普通地图命令字分离：

| 操作 | 普通地图命令字 | AVA战场命令字 |
|------|---------------|--------------|
| 移城 | fixed_move_city_new | lvl_move_city |
| 侦查玩家 | dispatch_scout | lvl_dispatch_scout_player |
| 侦查建筑 | dispatch_scout | lvl_dispatch_scout_building |
| 攻击玩家 | dispatch_troop | lvl_dispatch_troop |
| 攻击建筑 | dispatch_troop | lvl_dispatch_troop_building |
| 发起集结(玩家) | create_rally_war | lvl_create_rally_war |
| 发起集结(建筑) | create_rally_war_building | lvl_create_rally_war_building |
| 加入集结 | join_rally_war | lvl_join_rally_war |
| 解散集结 | rally_dismiss | lvl_rally_dismiss |
| 撤回集结部队 | recall_reinforce | lvl_recall_reinforce |
| 召回普通部队 | change_troop | lvl_use_troop_return_item |
| 从建筑召回 | - | lvl_change_troop |
| 行军加速 | - | lvl_use_troop_speed_up_item |
| 获取战场队伍信息 | - | lvl_battle_login_get |

### 当前活跃 AVA 战场（2026-03-18）

**战场 ID**: `lvl_id=29999`

| 项目 | 值 |
|------|-----|
| 战场 ID | 29999 |
| 已进入账号 | enemy_02 (20010669), acc_01 (20010643) |
| 阵营配置 | camp_id=1 (我方), camp_id=2 (敌方) |

### CLI 命令 - AVA 战场操作

```bash
# 查询账号所在战场
python src/main.py uid_ava_status <uid>

# 添加账号到战场名单（指定阵营）
python src/main.py uid_ava_add <lvl_id> <uid> <camp_id>

# 进入战场（需先添加到名单）
python src/main.py uid_ava_enter <lvl_id> <uid>
```

**完整迁移流程**：
```bash
# 示例：将账号迁移到 lvl_id=29999，阵营 1
python src/main.py uid_ava_add 29999 20010643 1    # 添加到名单
python src/main.py uid_ava_enter 29999 20010643     # 进入战场
python src/main.py uid_ava_status 20010643          # 验证状态
```

### 账号分布状态（2026-03-18）

**当前配置** (`config/accounts.yaml`)：
- 我方账号: 20个 (acc_01 到 acc_20, UID: 20010643-20010662)
- 敌方账号: 20个 (enemy_01 到 enemy_20, UID: 20010668-20010687)
- 备用账号: 21个 (reserves, UID: 20010413-20010432, 20010366, 20010373)

---

## 相关代码位置

- **API客户端**: `src/executor/game_api.py` — 包含所有游戏命令字方法
- **环境配置**: `config/env_config.yaml` — 服务器连接信息
- **账号配置**: `config/accounts.yaml` — 账号列表
- **小队配置**: `config/squads.yaml` — 按联盟分组的账号小队
- **主入口**: `src/main.py` — CLI 命令定义（包含 uid_helper 系列）
- **命令配置**: `src/config/cmd_config.yaml` — 所有命令字定义（含 AVA 相关）
- **检查脚本**: `scripts/check_ava_accounts.py` — AVA战场状态检查工具

## GM 指令 - 测试环境准备

### uid_helper 命令集

```bash
# 账号复制
python src/main.py uid_copy <src_uid> <tar_uid>

# 联盟管理
python src/main.py uid_create_al <name> <nick>        # 创建联盟
python src/main.py uid_join_al <aid> <uid1> [uid2...] # 加入+改名
python src/main.py uid_members <aid>                  # 查看成员

# 一站式准备
python src/main.py uid_setup <alliance_key> <src_uid> <tar_uid...>

# AVA 战场迁移
python src/main.py uid_ava_add <lvl_id> <uid> <camp_id>  # 添加到名单
python src/main.py uid_ava_enter <lvl_id> <uid>           # 进入战场
python src/main.py uid_ava_status <uid>                   # 查询状态
```
