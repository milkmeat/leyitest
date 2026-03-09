"""游戏服务器 HTTP 客户端

- Server-to-Server 内部HTTP接口，同步短连接
- 从配置读取UID列表直接操作，无需登录凭证
- 使用 aiohttp 实现异步并发请求
- 请求格式: POST /api/game  {"uid": "...", "cmd": "...", "params": {...}}
- 响应格式: {"code": 0, "msg": "ok", "data": {...}}
"""
