# Prompt Record

- Date: 2026-03-13 11:15
- Branch: master
- Commit: add 13 new command protocols (alliance, AVA, GM) with mock server handlers and param_overrides fix

---

### 1. 从 cmd_config_update.yaml 更新命令字配置

cmd_config_update中有一些新增的命令字协议，以此为准 更新/添加 我们的cmd_config.yaml，
所有新增协议在cli/mock server上测试通过

> **Insight**
> 对比分析结果：
> - 已存在且一致的命令：add_gem, move_city, add_soldiers, add_resource（无需改动）
> - 已存在但需更新的：get_player_info（update 拆分为两个命令）、scout_player（细微差异，保留现有更完整版本）
> - 新增命令共 12 个，分为三类：行动指令(attack_city)、感知查询(get_player_pos, get_al_members)、GM/准备指令(copy_player, change_name, join_alliance, create_alliance, al_leave, al_help_all, create_ava_battle, ava_add_player, ava_enter_battle)

**Files:** `src/config/cmd_config.yaml`, `mock_server/app.py`, `scripts/verify_cmds.py`

### 2. 提取 login_get 可用 section 列表

。ava_add_player
  的协议字段 uid 为什么改名为 target_uid?

> **Insight**
> 配置层（cmd_config.yaml）应忠实反映服务器协议，不该为了适配代码而篡改字段名。当代码接口和协议字段命名冲突时，应在代码层解决。给 send_cmd / queue_cmd 新增了 param_overrides: dict 参数 — 日常使用继续用 **kwargs 的便捷写法，只有字段名冲突时才用 param_overrides={"uid": xxx} 显式传 dict。

**Files:** `src/config/cmd_config.yaml`, `src/executor/game_api.py`, `mock_server/app.py`, `scripts/verify_cmds.py`

### 3. 提取 login_get 全部可选 section

cmd_config_update中有一些新增的命令字协议，以此为准 更新/添加 我们的cmd_config.yaml，
所有新增协议在cli/mock server上测试通过

你把 这个文件中所有的 "name": "svr_ghost_town_player_info" 这样格式的 信息都提取出来，记录到yaml文件中。作为login_get的可选参数说明

> **Insight**
> login_get 的 section 机制：服务器端存储了 252 个数据模块（section），通过 list 参数可按需拉取。这是一个典型的按需聚合查询设计 — 客户端根据场景选择性拉取数据，避免全量传输（全量约 136KB）。

**Files:** `src/config/login_get_sections.yaml`

### 4. 运行集成测试验证

测试一下 test_rally.sh 和 test_solo.sh

**Files:** (no changes, verification only)
