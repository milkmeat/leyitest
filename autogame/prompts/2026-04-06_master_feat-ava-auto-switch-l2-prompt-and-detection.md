# Prompt Record

- Date: 2026-04-06 00:00
- Branch: master
- Commit: feat: AVA 自动切换 — L2/L1 prompt 按 --ava 自动选择，get_player_info/sync 自动检测玩家地图位置

---

### 1. 实现 ava_switch.md 任务

实现ava_switch.md

> **Insight**
> 当前系统已有的 AVA 切换机制：
> - L0 执行层：`_AVA_ACTION_MAP` 根据 `default_header["lvl_id"]` 自动映射命令字（已完成）
> - L1 提示词：`l1_system_ava.txt` 已存在，通过 `--l1-prompt ava` 切换（已完成）
> - 缺口：L2 没有 AVA 提示词、sync 单账号不自动检测、get_player_info 不显示地图位置

> **Insight**
> 单账号 sync 和全量 sync 的区别：
> - `sync <uid>`：只拉玩家自身数据（兵种/英雄/坐标），不涉及地图 API，无需区分 AVA
> - `sync`（全量）：拉所有账号 + 地图数据，地图部分需要根据 `lvl_id` 切换 `game_svr_map_get` vs `lvl_svr_map_get`
> - 自动检测的意义：让用户知道玩家在哪个地图，方便后续操作时决定是否加 `--ava`

**Files:** `src/main.py`, `src/ai/l2_commander.py`, `src/controller/loop.py`, `src/ai/prompts/l2_system_ava.txt`, `todo/ava_switch.md`

### 2. L1 也自动切换 AVA prompt

l1_decide也会切换ava prompt吗

> **Insight**
> 现在 `--ava` 参数的行为在 L1 和 L2 层完全一致了：
> - 传 `--ava <lvl_id>` 时，L1 和 L2 都自动切换到 AVA prompt
> - 显式传 `--l1-prompt <name>` 仍然优先（覆盖自动切换）
> - 这意味着 `run --ava 29999` 一个参数就能同时切换 sync/L2/L1，不再需要额外加 `--l1-prompt ava`

**Files:** `src/main.py`, `src/controller/loop.py`

### 3. 更新 CLI help 信息

cli 的--help消息也更新一下

**Files:** `src/main.py`
