# Prompt Record

- Date: 2026-04-08 16:30
- Branch: master
- Commit: feat: L0 execute_batch 执行后自动采集最近 coal cart (10300)

---

### 1. L0 自动搜集 coal cart 需求

L0 自动搜集coal cart(10300): 如果执行完L0指令且不是移城的话，如果附近有coal cart, 派出一个队列搜集地图上最近的一个coal cart(10300)

> **Plan**
> 仅修改 `src/executor/l0_executor.py`：
> 1. 新增 `_auto_collect_coal_carts(self, uids: set[int])` 方法，位于 `_query_rally_id` 之后。逻辑：检查 AVA 模式 → 遍历 uid → 队列检查(march_type=21) → 查询地图 → 解析 briefObjs 提取玩家坐标和 10300 资源车 → 欧几里得距离找最近 → 调用 `lvl_collect_cart` 派遣采集。全程 try/except 隔离。
> 2. 在 `execute_batch` 末尾挂钩：收集所有有成功非移城指令的 uid，批量触发 `_auto_collect_coal_carts`。每个 uid 只查一次地图。

> **Insight**
> - 采集使用独立的 queue 6003 和专用命令 `lvl_dispatch_pick`（march_type=21），不占用战斗队列 6001/6002，所以可以在执行完战斗指令后"顺手"采集
> - 挂钩点选在 `execute_batch` 末尾而非每条指令后，是因为 `lvl_battle_login_get` 是一次完整的 HTTP 地图查询，per-uid 做一次就够了，避免重复网络开销
> - 采集全程 try/except 隔离，失败只写日志不影响 `results` 返回值，保证主战斗流程的稳定性

**Files:** `src/executor/l0_executor.py`
