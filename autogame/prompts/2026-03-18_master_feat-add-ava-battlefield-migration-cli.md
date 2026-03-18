# Prompt Record

- Date: 2026-03-18
- Branch: master
- Commit: feat: add AVA battlefield migration CLI commands

---

### 1. 使用 CLI 命令把 20010643 迁移到 ava 战场

用户要求使用 CLI 命令将指定 UID 迁移到 AVA 战场。当时没有现有的 CLI 命令支持此操作。

> **Insight**
> 1. **AVA 战场准入流程**：两步操作——先用 `op_lvl_set_player` 注册到名单（指定阵营），再用 `op_enter_lvl_battle` 正式进入
> 2. **阵营分配**：camp_id 决定战场中的归属，同一个 lvl_id 可以有两个对立阵营（通常是 1 和 2）
> 3. **错误码 27037**：之前的失败正是因为没有先在准入名单中注册

**Files:** `src/main.py`

### 2. 查询 enemy02 在哪个 ava 战场

用户想要查询 enemy_02 (UID: 20010669) 所在的 AVA 战场，以便将 20010643 迁移到同一战场。

查询结果显示 enemy_02 在 lvl_id=29999 的 AVA 战场。

### 3. 先要用 op_lvl_set_player 把 uid 添加到战场准入名单

用户指出迁移需要两步操作：先用 `op_lvl_set_player` 添加到战场名单，再用 `op_enter_lvl_battle` 进入。

当时第一次直接调用 `ava_enter_battle` 失败（错误码 27037），正是因为账号不在准入名单中。

> **Insight**
> 1. **两步迁移流程**：`op_lvl_set_player`（注册名单）→ `op_enter_lvl_battle`（正式进入），缺一不可
> 2. **参数冲突处理**：当命令参数名与 header 参数名相同时（如 `uid`），需用 `param_overrides` 字典传递
> 3. **战场验证机制**：通过对比进入前后的 `get_player_lvl_info` 返回值来确保迁移成功

**Files:** `src/main.py`

### 4. 阵营 ID 确认

> **Q:** 请告诉我 `camp_id` 是多少，或者我可以先尝试用 **1**？

用户确认使用 camp_id=1。

### 5. 把 ava lvl_id=29999 及必要的信息记录到 env-info skill

用户要求将当前活跃的 AVA 战场信息记录到 test-env-info skill 中，包括：
- 战场 ID (lvl_id=29999)
- 已进入的账号
- CLI 命令用法
- GM 指令集

> **Insight**
> 1. **知识持久化**：将环境关键信息记录到 skill 中，后续对话可通过 `/test-env-info` 快速查阅
> 2. **操作可追溯**：记录命令使用示例，方便团队成员复用相同流程
> 3. **集中式文档**：skill 作为单点真理，避免配置散落在多个文件中

**Files:** `.claude/skills/test-env-info/SKILL.md`
