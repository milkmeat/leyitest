## 目标
对cmd_config.yaml里面所有的命令，完成对应的python层封装

## 任务
- 我不知道对应的接口在test服务器上是否存在，可以先验证一下。如果不存在对应接口，标记一下告诉我，不需要进行后续的开发
- 对于可用接口，完成python命令字的支持，在命令行调用会返回有意义的结果，不报错。例如：  python main.py <command> <uid>
- 对于可用接口，也完成mock server的开发测试。如果是数据查询，需要和mock_data里面的值一样。如果是数据添加（如add_resource），需要看调用前后的数字变化。

## 要求
- 如有不明确的项目，一开始就向我询问，并更新本文件
- 都明确后，先分解成适当的工作项，更新本文件。开始开发调试
- 每个工作项进度完成后，更新本文件
- 所有新完成的命令字，都要在mock server上测试通过

---

## 接口验证结果

**全部 17 个命令在 test 服务器上均可用** (验证时间: 2026-03-10)

| 命令 | 服务器命令字 | test服务器 | 状态 |
|------|-------------|-----------|------|
| move_city | fixed_move_city_new | ✅ ret_code=0 | 可用 |
| attack_player | dispatch_troop | ✅ 有 res_data | 可用 |
| attack_building | dispatch_troop | ✅ 有 res_data | 可用 |
| reinforce_building | dispatch_troop | ✅ 有 res_data | 可用 |
| scout_player | dispatch_scout | ✅ 有 res_data | 可用 |
| create_rally | create_rally_war | ✅ 有 res_data | 可用 |
| join_rally | dispatch_troop | ✅ 有 res_data | 可用 |
| recall_reinforce | recall_reinforce | ✅ 有 res_data | 可用 |
| recall_troop | change_troop | ✅ 有 res_data | 可用 |
| get_all_player_data | game_server_login_get | ✅ ret_code=0 | 可用 |
| get_player_info | login_get | ✅ ret_code=0 | 已有 |
| get_map_overview | get_map_brief_obj | ✅ 有 res_data (30100) | 可用(需要正确sid) |
| get_map_detail | game_svr_map_get | ✅ 有 res_data (30100) | 可用(需要正确sid) |
| get_battle_report | get_city_battle_report | ✅ 有 res_data | 可用 |
| add_gem | op_self_set_gem | ✅ ret_code=0 | 可用 |
| add_soldiers | op_add_soldiers | ✅ ret_code=0 | 可用 |
| add_resource | op_self_add_clear_resource | ✅ ret_code=0 | 可用 |

## 工作项分解与进度

### 1. ✅ 验证 test 服务器接口可用性
- 编写 `scripts/verify_cmds.py` 自动验证所有 17 个命令
- 结果：全部可用，无需排除任何命令

### 2. ✅ CLI 命令支持 (src/main.py)
新增 15 个 CLI 命令（原有 get_player_pos + get_player_info 共 2 个）：

**查询命令:**
- `get_all_player_data <uid>` — 解析并展示全量数据（分模块 JSON）
- `get_map_overview <uid>` — 地图缩略信息
- `get_map_detail <uid> [bid...]` — 地图区块详细信息
- `get_battle_report <uid> <report_id>` — 战报查询

**行动命令:**
- `move_city <uid> <x> <y>` — 移城并验证结果
- `attack_player <uid> <target_uid> <x> <y>` — 攻击玩家
- `attack_building <uid> <building_id> <x> <y>` — 攻击建筑
- `reinforce_building <uid> <building_id> <x> <y>` — 驻防建筑
- `scout_player <uid> <target_uid> <x> <y>` — 侦察玩家
- `create_rally <uid> <target_id> [prepare_time]` — 发起集结
- `join_rally <uid> <rally_id>` — 加入集结
- `recall_troop <uid> <troop_id...>` — 召回行军部队
- `recall_reinforce <uid> <unique_id>` — 召回增援/集结

**GM 命令:**
- `add_gem <uid> [amount]` — 添加宝石（显示当前宝石数）
- `add_soldiers <uid> [soldier_id] [num]` — 添加士兵（显示当前士兵列表）
- `add_resource <uid> [op_type]` — 添加资源

### 3. ✅ Mock Server 处理器 (mock_server/app.py)
新增 13 个命令处理器（原有 login_get 1 个）：

| 处理器函数 | 处理的命令字 | 功能 |
|-----------|-------------|------|
| handle_game_server_login_get | game_server_login_get | 返回全量玩家数据 |
| handle_fixed_move_city_new | fixed_move_city_new | 更新玩家坐标+召回部队 |
| handle_dispatch_troop | dispatch_troop | 攻击/驻防/加入集结，生成 troop |
| handle_dispatch_scout | dispatch_scout | 侦察目标位置的玩家 |
| handle_create_rally_war | create_rally_war | 创建集结，存入内存 |
| handle_recall_reinforce | recall_reinforce | 从 troops/rallies 中移除 |
| handle_change_troop | change_troop | 召回指定 ID 的部队 |
| handle_get_map_brief_obj | get_map_brief_obj | 返回地图上所有对象概览 |
| handle_game_svr_map_get | game_svr_map_get | 返回建筑详细信息 |
| handle_get_city_battle_report | get_city_battle_report | 返回战报（或错误） |
| handle_op_self_set_gem | op_self_set_gem | 设置宝石数量 |
| handle_op_add_soldiers | op_add_soldiers | 增加士兵数量 |
| handle_op_self_add_clear_resource | op_self_add_clear_resource | 添加资源 |

### 4. ✅ Mock Data 扩展 (mock_server/mock_data.yaml)
- 玩家数据增加: alliance_id, city_level, lord_level, vip_level, gem, soldiers详情, heroes详情
- 新增建筑数据: 2个据点 (Alpha, Beta)
- 新增动态数据结构: troops, reinforcements, rallies, battle_reports

### 5. ✅ Mock Server 测试
全部 17 个命令通过 mock server 测试：
- 查询命令: 返回与 mock_data 一致的数据
- 行动命令: 正确修改内存状态（如移城更新坐标、部队调度增减 troops）
- GM命令: 正确修改数据（add_gem/add_soldiers 可见数值变化）
- 错误处理: 无效ID返回正确错误码（30001/30113）

## 修改文件列表
- `src/main.py` — 新增 15 个 CLI 命令函数和注册
- `mock_server/app.py` — 新增 13 个命令处理器，增加辅助函数
- `mock_server/mock_data.yaml` — 扩展测试数据
- `scripts/verify_cmds.py` — 新增接口验证脚本（工具）
- `scripts/dump_responses.py` — 新增响应结构分析脚本（工具）
