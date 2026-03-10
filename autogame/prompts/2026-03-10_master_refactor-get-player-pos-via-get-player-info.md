# Prompt Record

- Date: 2026-03-10 21:00
- Branch: master
- Commit: refactor: get_player_pos delegates to get_player_info with optional modules param

---

### 1

重构一下，从cmd_config.yaml和game_api.py里面去掉 get_player_pos 命令。让这个命令在python层调用get_player_info，并解析pos信息。get_player_info()允许传入可选参数：例如仅传入svr_lord_info_new可以减少网络信息传递（不指定的话默认读取list中的全部模块）

> **Insight**
> **这次重构的关键设计决策：**
> 1. `get_player_info(modules=...)` 通过 `overrides` 机制覆盖 `cmd_config.yaml` 中的 `list` 默认值。`send_cmd` 已有的 `build_param` + `overrides` 机制天然支持这个需求，无需新增基础设施
> 2. `get_player_pos` 变成了 `get_player_info` 的薄封装——只请求 `svr_lord_info_new` 一个模块，网络传输量和之前独立命令完全一致
> 3. 从 `cmd_config.yaml` 中删除 `get_player_pos`，消除了两个命令字做同一件事的冗余

**Files:** `src/config/cmd_config.yaml`, `src/executor/game_api.py`
