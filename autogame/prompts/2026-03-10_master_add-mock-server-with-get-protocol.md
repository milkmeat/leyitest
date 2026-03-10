# Prompt Record

- Date: 2026-03-10 00:00
- Branch: master
- Commit: add mock server with GET protocol support and --mock CLI flag

---

### 1

你来完成 firs_mock_server.md

> **Insight**
> **项目中有两套协议**：
> 1. `client.py` 使用 **GET + URL 拼 JSON** 协议（真实 test 服务器）
> 2. `game_api.py` 使用 **POST /api/game** 协议（设计给未来的 mock server）
>
> 验收标准用的是 `client.py`（即 GET 协议），所以 mock server 需要兼容这个 GET 协议。
>
> **坐标编码公式**：`city_pos = x * 100_000_000 + y * 100`
> 例如 (123, 234) → `12300023400`

**Files:** `mock_server/app.py`, `mock_server/mock_data.yaml`, `config/env_config.yaml`, `src/main.py`, `src/client.py`, `todo/done/first_mock_server.md`
