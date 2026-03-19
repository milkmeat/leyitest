# Prompt Record

- Date: 2026-03-19
- Branch: master
- Commit: feat: add AVA battlefield leave CLI command

---

### 1. 使用 CLI 命令把账号迁移到 AVA 战场

用户要求使用 CLI 命令将 UID 20010643 迁移到 AVA 战场。

执行了完整的两步迁移流程：
1. `uid_ava_add 29999 20010643 1` - 添加到 lvl_id=29999 战场名单，阵营 1
2. `uid_ava_enter 29999 20010643` - 正式进入战场
3. `uid_ava_status 20010643` - 验证状态

迁移成功，账号从普通地图 (lvl_id=0) 进入到 AVA 战场 (lvl_id=29999)。

### 2. 使用 CLI 命令让账号离开 AVA 战场

用户要求使用 leave_lvl_battle 命令让 UID 20010643 离开 AVA 战场。

当时没有现成的 `uid_ava_leave` CLI 命令。在 cmd_config.yaml 中发现 `ava_leave_battle` 命令字定义，但缺少对应的 CLI 入口。

添加了 `cmd_uid_ava_leave` 函数和命令注册，实现了离开战场功能。

**Files:** `src/main.py`

### 3. 第一次尝试使用错误的命令字

> **Q:** 用户反馈修改了 cmd_config.yaml，将命令字改为 "op_leave_lvl_battle"

尝试使用 `op_leave_lvl_battle` 命令字，但服务器返回错误码 30000："cannot find desc in cmd_def"，说明服务器端没有这个命令字定义。

**Files:** `src/config/cmd_config.yaml`

### 4. 修改配置使用 extra_header 机制

> **Q:** 用户反馈修改了 ava_leave_battle 的 yaml 文件，需要额外的 header 参数

用户修改了 cmd_config.yaml，使用正确的命令字 `leave_lvl_battle`，并添加了 `extra_header` 配置，需要在 HTTP header 中传入 `lvl_id` 参数。

修改了 `cmd_uid_ava_leave` 函数，在调用 `send_cmd` 时通过 `header_overrides` 传递当前战场 ID：

```python
resp = await client.send_cmd("ava_leave_battle", uid, header_overrides={"lvl_id": before_lvl})
```

执行成功，账号从 AVA 战场 (lvl_id=29999) 返回到普通地图 (lvl_id=0)。

> **Insight**
> 1. **extra_header 机制**：某些命令字需要在 HTTP header 中传递额外参数（如 `lvl_id`），这些参数通过 `header_overrides` 字典传递给 `send_cmd()`
> 2. **动态参数获取**：由于账号当前所在的战场 ID 是动态的，我们先用 `get_player_lvl_info()` 获取，再通过 `header_overrides` 传递
> 3. **战场进入/离开流程**：进入需要 `op_lvl_set_player` → `op_enter_lvl_battle`，离开只需 `leave_lvl_battle` + header 中的 `lvl_id`

**Files:** `src/main.py`, `src/config/cmd_config.yaml`
