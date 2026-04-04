# Prompt Record

- Date: 2026-04-04 16:30
- Branch: master
- Commit: feat: 补全 game_svr_map_get 普通地图地块详情查询（含 bid 计算、格式化 CLI、响应解析）

---

### 1. 补全 game_svr_map_get 命令

与lvl_svr_map_get的命令并列的，还有一个game_svr_map_get（get_map_detail）命令，用于获取普通地图上的信息。补充相应的yaml,       pyhton api, cli命令，完成这一命令字。在test server上测试通过

> **Plan**
> `game_svr_map_get` 已有基础骨架（YAML 配置 + 裸 API 方法 + 简单 CLI），但功能远不如其 AVA 对应版本 `lvl_svr_map_get`。需要补齐：
> 1. `src/executor/game_api.py` — 新增 `get_map_area()` wrapper（自动 bid 计算 + 响应解析），修复 `get_map_detail()` 的 sid 默认值和 lvl_id:0 header
> 2. `src/main.py` — 重写 `cmd_get_map_detail` CLI 为坐标驱动 + 格式化输出，更新 COMMANDS 注册
> 3. `src/config/cmd_config.yaml` — sid 默认值改为 1，更新 description

> **Insight**
> - 普通地图和 AVA 战场共用同一套 header 模板，`lvl_id` 字段决定路由：非零→战场服务器，零→普通地图服务器。这是 30100 网络错误的根因。
> - 普通地图的对象类型体系 (2=玩家城, 6=资源点, 12=联盟资源点) 与 AVA (10101=玩家城, 10001=建筑, 101=行军) 完全不同，但响应结构 (`mapBidObjs → objs → objBasic`) 一致。

**Files:** `src/executor/game_api.py`, `src/main.py`, `src/config/cmd_config.yaml`
