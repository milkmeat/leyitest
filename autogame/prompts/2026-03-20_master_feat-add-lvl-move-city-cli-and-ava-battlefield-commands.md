# Prompt Record

- Date: 2026-03-20
- Branch: master
- Commit: feat: add lvl_move_city CLI command and AVA battlefield commands support

- Add CLI command lvl_move_city with lvl_id parameter support
- Add extra_header configuration for all AVA battlefield commands (15 commands)
- Add CLI functions for common AVA commands: lvl_scout_player, lvl_scout_building, lvl_attack_player, lvl_attack_building, lvl_rally_dismiss
- Add target_type and key parameter support for lvl_attack_building
- Auto-extract target_type from building_id (e.g., '10006_xxx' -> 10006)
- Add detailed request logging on failure (Header, Request, URL)
- Update --help output with new 'AVA 战场行动' section
- Modify game_api.py methods to accept lvl_id and pass via header_overrides

---

### 1. Add lvl_move_city CLI command

用户要求在 CLI 中增加支持命令 `lvl_move_city`，其格式和普通 `move_city` 一样。

> **Insight**
> - CLI 命令模式：帮助文本 → 处理函数 → 命令字典注册
> - `lvl_move_city` 是 AVA 战场的移城命令，底层使用不同的游戏命令字
> - 保持与 `move_city` 相同的参数格式确保用户体验一致

**Files:** `src/main.py`

### 2. Update --help output for lvl_move_city

用户要求更新 --help 输出的帮助信息。

> **Insight**
> - 双重帮助来源：模块 docstring（IDE 显示用）+ main 函数动态输出（CLI 用）
> - 命令列表硬编码：为了控制分组顺序，main 函数中使用硬编码列表而非动态遍历
> - 修改一致性好：两处都已更新（第 28 行 docstring + 第 1588 行 main 函数）

**Files:** `src/main.py`

### 3. Add detailed request logging on failure

用户要求在请求失败的时候，把本次发送的 header/request 都打印出来。

> **Insight**
> - 错误调试三要素：请求头（身份）、请求体（内容）、响应/异常（原因）
> - aiohttp 异常类型：`ClientError` 基类覆盖网络/协议/超时等所有失败场景
> - 结构化日志：使用 JSON 格式打印便于后续分析和复现

**Files:** `src/executor/game_api.py`

### 4. Sync extra_header configuration for all AVA commands

用户修改了 cmd_config.yaml，给 lvl_move_city 增加了 extra_header，要求同步更新其余代码，把所有 ava_ 开头的命令都修改一下，yaml 里面带上 extra_header，模仿 lvl_move_city 命令都做响应修改：`extra_header: {lvl_id: "战场ID"}`。

> **Insight**
> - **配置驱动**：YAML 中声明 `extra_header: {lvl_id: "战场ID"}`，自动提示需要此参数
> - **参数透传**：所有便捷方法添加 `lvl_id` 参数，通过 `header_overrides` 注入到请求头
> - **验证输出**：可以看到 Header 中正确包含了 `lvl_id: 1`

**Files:** `src/config/cmd_config.yaml`, `src/executor/game_api.py`

### 5. Show more AVA commands in --help

用户说 --help 信息里面很多 ava 命令还看不到，要求显示更多 AVA 战场命令。

> **Insight**
> - **分类管理**：将普通地图命令和 AVA 战场命令分开显示，结构更清晰
> - **新增 CLI 函数**：`cmd_lvl_scout_player`, `cmd_lvl_scout_building`, `cmd_lvl_attack_player`, `cmd_lvl_attack_building`, `cmd_lvl_rally_dismiss`
> - **三层同步**：模块 docstring、命令字典、main 函数输出都已更新

**Files:** `src/main.py`

### 6. Add target_type parameter to lvl_attack_building

用户要求给 `lvl_attack_building` 命令添加一个 `target_type` 命令参数。

**Files:** `src/executor/game_api.py`, `src/main.py`

### 7. Auto-extract target_type from building_id

用户要求默认值使用 building_id 用 _ 分割的第一段：`10006_1773137411102403` -> `10006`。

> **Insight**
> - **智能解析**：从 `building_id` 第一段提取 `target_type`（如 `"10006_xxx"` → `10006`）
> - **回退机制**：如果解析失败，使用默认值 `10001`
> - **可覆盖**：手动指定 `target_type` 参数可覆盖自动提取的值

**Files:** `src/main.py`

### 8. Pass key parameter in CLI for lvl_attack_building

用户询问 CLI 调用 `lvl_attack_building` 时，`target_info.key` 怎么传递进去。

> **Insight**
> - **参数解析**：使用 `*extra` 可变参数，根据数量判断 `target_type` 和 `key`
> - **三种用法**：5/6/7 个参数分别对应不同的参数组合
> - **传递顺序**：`target_type` 和 `key` 会正确传递到 `target_info.key` 中

**Files:** `src/main.py`
