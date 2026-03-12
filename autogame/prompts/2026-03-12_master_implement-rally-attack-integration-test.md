# Prompt Record

- Date: 2026-03-12 22:00
- Branch: master
- Commit: implement rally attack integration test with CLI command upgrades

---

### 1. Complete rally attack test task

你来完成 todo\test_l0_rally_attack.md

> **Insight**
> **发现关键问题**：当前 `cmd_create_rally` 和 `cmd_join_rally` 的 CLI 实现过于简单：
> 1. `create_rally` 没有构造正确的 `target_info`（缺少 `pos`，id格式应为 `2_{uid}_1`）
> 2. `march_info` 传了空 `{}`，服务器要求包含士兵数据
> 3. `join_rally` 同样缺少 march_info 的士兵数据
> 需要参照 `attack_player` 的实现模式来修复这两个命令。

> **Insight**
> **集结前置条件确认**：
> - `create_rally` 要求发起者��联盟中
> - `join_rally` 要求加入者与队长在同一联盟
> - 这是游戏逻辑限制，mock server 不做此校验所以可以先在 mock 上开发测试

> **Insight**
> **Mock 测试全部通过！** 关键技术点：
> 1. **rally_id 提取**：mock server 返回的 rally_id 嵌套在 stringified JSON 中（`\"rally_id\": \"rally_xxx\"`），用 `rally_\d+_\d+` 正则模式匹配最为可靠
> 2. **auto-create player**：GM 命令（add_gem/add_soldiers）改用 `_get_or_create_player` 后，mock server 不再需要预先配置玩家数据
> 3. **SKIP 是预期的**：6 个 SKIP 都是士兵减少验证，因为 mock 环境没有战斗结算引擎

**Files:** `src/main.py`, `src/executor/game_api.py`, `src/config/cmd_config.yaml`, `mock_server/app.py`, `test_rally.sh`, `todo/test_l0_rally_attack.md`

### 2. Rally requires alliance membership

> **Q:** create_rally 在 test server 上持续返回 ret_code=30001（空错误消息）。attack_player 同样条件下可以成功。是否需要前置条件才能使用集结功能？

需要在联盟中才可以发起rally，同一个联盟的成员才可以发起增援。你可以先用mock测试，我来配置test server
