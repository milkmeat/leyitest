# Prompt Record

- Date: 2026-03-10 00:00
- Branch: master
- Commit: add game client and CLI to query player position from test server

---

### 1

你来完成 todo/can_connect_to_test_server.md

> **Insight**
> **关键发现：两套协议完全不同**
> 1. 参考项目连接真实测试服务器，使用 **GET 请求 + URL 拼接 JSON body** 的方式（类似 JSONP 风格）
> 2. autogame 现有的 `game_api.py` 是为 mock server 设计的，用 **POST /api/game + JSON payload**
> 3. 坐标编码公式 `pos = x * 100_000_000 + y * 100`，两个项目一致，可复用 `game_api.py` 中的 `decode_pos`

**Files:** `config/env_config.yaml`, `src/client.py`, `src/main.py`, `todo/can_connect_to_test_server.md`

### 2

文档写错了，应该是 python src/main.py get_player_pos 20001946
文档和代码都改一下

**Files:** `src/main.py`, `todo/can_connect_to_test_server.md`

### 3

完成了的todo md文件，移动到 todo/done/下面

**Files:** `todo/done/can_connect_to_test_server.md`
