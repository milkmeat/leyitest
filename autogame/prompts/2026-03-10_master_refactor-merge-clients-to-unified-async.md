# Prompt Record

- Date: 2026-03-10 22:30
- Branch: master
- Commit: refactor: merge client.py and game_api.py into unified async GET client

---

### 1

Implement the following plan:

# 重构：合并 client.py 和 game_api.py 为统一客户端

## Context

项目中有两个游戏服务器 HTTP 客户端：
- `src/client.py` (GameClient) — 同步，GET 协议，有环境切换，仅 CLI 使用
- `src/executor/game_api.py` (GameAPIClient) — 异步，POST 协议（死代码），有便捷方法和批量队列

现在 mock server 和真实服务器都走 GET 协议，POST 协议无人使用。两个客户端共享大量逻辑（cmd_config 加载、参数构建）。合并为一个统一的异步客户端。

## 改动计划

### 1. 修改 `src/executor/game_api.py` — 统一客户端

- **`_send()` 改为 GET 协议**：从 `GameClient` 搬过来 header/extra_info/GET 拼 JSON 的逻辑，替换掉 POST `/api/game`
- **构造函数改为环境驱动**：加载 `env_config.yaml`，接受 `env` 参数（替代硬编码 `base_url`）
- **保留所有现有便捷方法**（move_city, attack_player 等）和批量队列能力
- **添加响应解析方法**：把 `client.py` 中 `get_player_pos` 的解析逻辑移入 `get_player_pos()` 便捷方法，直接返回 `(x, y)` 而非原始 JSON

### 2. 修改 `src/main.py` — 改用 GameAPIClient

- `from src.executor.game_api import GameAPIClient`
- 用 `asyncio.run()` 包装异步调用
- 删除对 `src.client` 的 import

### 3. 删除 `src/client.py`

不再需要。

### 4. 修改 `mock_server/app.py`（如需要）

检查是否有对 client.py 的依��，预计无。

## 关键文件

- `src/executor/game_api.py` — 主要修改
- `src/main.py` — 适配修改
- `src/client.py` — 删除
- `config/env_config.yaml` — 不变（已有 test + mock 环境）
- `src/config/cmd_config.yaml` — 不变

## 验证

```bash
# 启动 mock server
python mock_server/app.py

# 测试 mock
python src/main.py --mock get_player_pos 20001946
# 期望: (123,234)

# 测试 test 服务器
python src/main.py get_player_pos 20001946
# 期望: (170,178)
```

> **Insight**
> - **两个客户端的核心差异**：`client.py` 用同步 `requests.get` + GET 协议（URL 拼 JSON），`game_api.py` 用异步 `aiohttp.post` + POST 协议。真实服务器和 mock 都走 GET，所以 POST 是死代码。
> - **合并策略**：把 `client.py` 的 GET 协议逻辑搬进 `game_api.py` 的 `_send()`，再加上 `env_config.yaml` 环境驱动，就能完全替代两个客户端。
> - **`get_player_pos` 的响应解析**非常深层嵌套（`res_data[0].push_list[0].data[] → JSON str → lord_info`），这个逻辑需要作为便捷方法保留在统一客户端中。
> - **GET 协议的特殊之处**：这个游戏后台的"GET 协议"实际上是把整个 JSON body 作为 query string 直接拼在 URL 后面（`?{json}`），而非标准的 `?key=value` 形式。
> - **环境驱动 vs 硬编码 URL**：旧的 `GameAPIClient` 要求传入 `base_url` 字符串。新版通过 `env` 参数间接查 `env_config.yaml`，实现了配置集中管理。
> - **`get_player_pos` 返回类型变化**：从返回原始 `Dict` 变为返回 `Optional[Tuple[int, int]]`，这是一个 breaking change，但当前只有 `main.py` 使用，所以安全。

**Files:** `src/executor/game_api.py`, `src/main.py`, `src/client.py`
