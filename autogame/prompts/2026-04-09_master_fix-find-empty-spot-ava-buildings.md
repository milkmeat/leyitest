# Prompt Record

- Date: 2026-04-09 11:48
- Branch: master
- Commit: fix: _find_empty_spot 修正 AVA 建筑碰撞检测（类型补全+左下角模型+资源车1x1+欧氏排序）

---

### 1. 测试 L0 移城到 AVA 建筑坐标

测试：使用L0命令将20010643 移城到 ava=29999 的 114,196 坐标

> **Insight**
> - 直接用 `lvl_move_city` 命令发到 (114,196) 会失败（21105 = 目标位置被占），因为那里有个 type=10000 的建筑
> - 用 `l0 LVL_MOVE_CITY` 走 L0 执行器，它先尝试原坐标失败后，自动调用 `_find_empty_spot` 做 AABB 碰撞检测，按切比雪夫距离由近到远搜索空位
> - 最终找到 (107, 195) 作为最近可用空位，移城成功（`ret_code: 0`）

**Files:** `src/executor/l0_executor.py`

### 2. 指出更近的位置未被选中

其实还有更近的位置例如113,198，为什么没有选中

> **Insight**
> - 根因：`_OBSTACLE_TYPES` 缺少 AVA 建筑类型 (10000, 10001, 10002, 10006, 10103, 10104)，导致智能搜索"看不见"这些建筑，误判目标为空位
> - 修复后螺旋搜索正常工作，从距离 0 开始逐层扩展，找到距离 3 的最近合法位置
> - type=10000 建筑占 4 格，城池占 5 格，两者 AABB 碰撞检测需要间隔至少 3 格才不重叠

**Files:** `src/executor/l0_executor.py`

### 3. 指出螺旋搜索起点离目标太远

螺旋搜索的起点好像离目标太远了

> **Insight**
> - 同一切比雪夫环 r=3 上，(-3,-3) 和 (-3,0) 都是距离 3，但欧氏距离差别很大（4.24 vs 3.0）
> - 加了 `candidates.sort(key=lambda c: dx²+dy²)` 后，正交方向（上下左右）优先于对角方向
> - 对实战意义：移城后离目标建筑更近，行军时间更短

**Files:** `src/executor/l0_executor.py`

### 4. 螺旋搜索步长改为 2

螺旋搜索每一圈设置成2

**Files:** `src/executor/l0_executor.py`

### 5. 指出坐标是左下角而非中心

ava地图上的建筑，不是以坐标点为圆心分布的。坐标点指的是其所占据矩形的左下角

**Files:** `src/executor/l0_executor.py`

### 6. 指出资源车占地为 1x1

资源车是1x1

**Files:** `src/executor/l0_executor.py`
