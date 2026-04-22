# Prompt Record

- Date: 2026-04-22 10:10
- Branch: master
- Commit: fix: 消除 REINFORCE_BUILDING (0,0) 坐标导致的驻防失败（坐标补全+安全网）

---

### 1. 分析 fix_reinforce_building_invalid_coords 问题

阅读 fix_reinforce_building_invalid_coords.md，检查当前logs/目录下最新日志，看问题是否仍然存在，如何修复

> **Plan**
> 修复方案（单文件修改 `src/executor/l0_executor.py`）：
> - Fix 1: 坐标补全 — 在 `_preprocess_lvl_attack_building` 的 troop 去重之后、距离检查之前，插入坐标解析：当 `target_x/target_y` 为 0 时从 `self._buildings` 缓存获取建筑坐标
> - Fix 2: (0,0) 安全网 — 距离检查触发移城转换时，如果坐标仍为 (0,0)，跳过移城转换直接放行
> - 不修改 L1 prompt（坐标对 REINFORCE 确实是可选的，bug 在 L0）
> - 不修改 `needs_coords` 验证集（加了会拒绝合法指令）
>
> 根因链：
> 1. L1 prompt 正确地告诉 AI target_x/target_y 对 REINFORCE 是可选的（API 用 pos="nil"）
> 2. L0 验证只检查 building_id 非空，不要求坐标
> 3. L0 预处理用 (0,0) 做距离计算 → 触发 MOVE_CITY 转换 → 移城到 (0,0) 失败
> 4. 坐标从 building_id 解析的逻辑只存在于 INITIATE_RALLY，REINFORCE 没有
> 5. JOIN→REINFORCE 转换也不设置坐标，同样产生 (0,0) 问题

> **Insight**
> 这个 bug 的本质是"接口层与预处理层的坐标契约不一致"：游戏 API 层设计了 `pos="nil"` 让服务器按 building_id 定位，所以 REINFORCE 不需要坐标；但 L0 预处理层（距离检查 + 移城转换）假设所有指令都有有效坐标。两层之间缺少一个"坐标补全"桥接。

> **Insight**
> 修复前 vs 修复后：修复前 REINFORCE (0,0) → 距离检查触发 → 转 MOVE_CITY (0,0) → 移城失败。修复后 REINFORCE (0,0) → Fix 1 坐标补全 / Fix 2 安全网 → 直接发送 lvl_dispatch_troop (pos="nil") → 服务器按 building_id 定位。剩余 23 个失败全部是 queueid=6001 has occupied，属于独立的队列占用问题。

**Files:** `src/executor/l0_executor.py`, `todo/fix_reinforce_building_invalid_coords.md`
