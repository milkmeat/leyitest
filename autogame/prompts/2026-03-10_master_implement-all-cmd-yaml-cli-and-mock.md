# Prompt Record

- Date: 2026-03-10 19:00
- Branch: master
- Commit: implement CLI and mock server for all cmd_config.yaml commands

---

### 1

你来完成 add_cmd_yaml_implementation.md

> **Insight**
> - `cmd_config.yaml` 定义了 **17 个命令**，`game_api.py` 中已有全部 17 个语义封装方法
> - 但 CLI（`main.py`）只暴露了 2 个命令（`get_player_pos`, `get_player_info`）
> - Mock Server 只实现了 1 个处理器（`login_get`）
> - 所以核心工作是：验证 test 服务器接口 → 补全 CLI 入口 → 补全 Mock Server 处理器
>
> - test 服务器对所有命令都返回了统一的 `{res_header, request, res_data}` 结构
> - 即使参数不完全正确（如虚假的 rally_id），服务器也不会报 HTTP 错误，而是在 `res_data` 中返回业务错误码
> - 这意味着所有 17 个命令字接口都存在且可用，我们可以全部实现
>
> - **Mock Server 的有状态设计**：与简单的请求/响应模拟不同，这个 mock server 在内存中维护了可变状态（玩家位置、部队列表、宝石数量等）。`dispatch_troop` 会往 `troops` 列表追加，`recall_troop` 会从中移除，`move_city` 会更新坐标并清空部队——这使得我们能验证操作前后的数据一致性。
> - **CLI 的 `*extra` 参数模式**：对于有可选参数的命令（如 `add_gem <uid> [amount]`），使用 `*extra: str` 捕获变长参数，再按位置解析。这比用 argparse 更轻量，适合这种每个命令参数结构固定的场景。
> - **命令字复用**：`dispatch_troop` 一个后端命令字服务了 4 个不同语义的操作（attack_player, attack_building, reinforce_building, join_rally），通过 `march_type` 和 `target_type` 区分。Mock Server 的单一 handler 优雅地处理了这种复用。

**Files:** `src/main.py`, `mock_server/app.py`, `mock_server/mock_data.yaml`, `scripts/verify_cmds.py`, `scripts/dump_responses.py`, `todo/add_cmd_yaml_implementation.md`
