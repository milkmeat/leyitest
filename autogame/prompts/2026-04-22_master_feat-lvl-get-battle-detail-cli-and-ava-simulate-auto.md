# Prompt Record

- Date: 2026-04-22 15:30
- Branch: master
- Commit: feat: 添加 lvl_get_battle_server_detail CLI + ava_simulate 自动选战场/日志归档

---

### 1. 暴露 lvl_get_battle_server_detail 到 CLI

把 lvl_get_battle_server_detail 命令暴露到cli

> **Insight**
> `get_ava_score` 命令内部同时调用了 `lvl_battle_login_get` + `lvl_get_battle_server_detail` 并做了格式化输出。但有时你只想看原始的 `svr_lvl_war_situation_detail` 数据，不需要阵营汇总的混合视图。独立暴露这个命令可以方便调试积分排行的原始数据结构。

**Files:** `src/main.py`

### 2. 修改命令不需要 uid 参数

"python src/main.py lvl_get_battle_server_detail  29999" 这个命令不需要uid的，只要战场id就可以检测战场是否存在

> **Plan**
> 修改 `cmd_lvl_get_battle_server_detail` 函数签名去掉 `uid_str` 参数，只保留 `lvl_id_str`。使用 GM uid（`gm_uid = 20010643`，同 `cmd_uid_ava_create` 模式）作为 header 身份。更新 COMMANDS 注册表参数说明。

> **Insight**
> 这类"查询型"GM 命令不需要真实玩家身份，用固定 `gm_uid = 20010643` 即可。这是项目中 `cmd_uid_ava_create` 等命令已有的模式。

**Files:** `src/main.py`

### 3. 增强 ava_simulate.sh：自动选战场 + 日志归档

给 @ava_simulate.sh 加上以下功能：
  1. 自动选择 ava 战场id，不需要在参数中指定
  2. 在脚本中，使用 "python src/main.py lvl_get_battle_server_detail 29999"
  命令可以检测战场是否存在
  3. 从40001开始，每次+1，找到第一个未使用的空闲ava_id，创建一个全新战场用于测试
  4. 启动对战之前， 做这个操作将旧的日志归档：mv logs logs.<timestamp>
  5. 完成后， "./ava_simulate.sh 60" 即可启动一个小时的ava对战测试，并且logs下面只有最新一轮测试的日志

> **Plan**
> 1. 修改参数解析：`ava_id` 不再是必选参数，用法变为 `./ava_simulate.sh [duration_minutes]`
> 2. 新增 `find_free_ava_id()` 函数：从 40001 开始探测，调用 `lvl_get_battle_server_detail` 检测，输出含 `[OK]` 则跳过，否则该 ID 可用
> 3. 在 Step 1 之前调用 `find_free_ava_id` 自动确定 `AVA_ID`
> 4. 新增日志归档步骤：对战启动前 `mv logs logs.<timestamp>`，然后 `mkdir -p logs`

> **Insight**
> `find_free_ava_id` 的探测输出（"已存在，跳过"）走 stderr，只有最终选定的 ID 走 stdout，这样 `AVA_ID=$(find_free_ava_id)` 能干净地捕获数字，同时用户仍能看到探测过程。日志归档放在对战启动前，确保准备阶段的日志不会丢失。

**Files:** `ava_simulate.sh`
