"""Mock 游戏服务器 — FastAPI 应用

单一入口 POST /api/game，与真实游戏服务器接口格式一致。
维护有状态的内存世界，模拟行军、战斗、据点占领等游戏行为。

调试工具:
- --speed 10x  快进模式
- --pause      暂停/步进模式
- POST /debug/set_state  运行时状态注入
"""
