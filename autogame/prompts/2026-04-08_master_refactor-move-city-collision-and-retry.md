# Prompt Record

- Date: 2026-04-08 20:00
- Branch: master
- Commit: refactor: 移城空位搜索改为 AABB 碰撞检测，重试策略改为1次智能+3次随机

---

### 1. 确认移城重试逻辑是否存在

现在还有 ava移城 重试3次智能搜索空位 逻辑吗？

### 2. 移城碰撞检测与重试策略改造需求

1. _find_nearest_empty_spot: 主城和各种ava建筑都有自己的宽度。主城半径是2，steam factory会占据 139,155 - 145,161 之间的矩形，其余建筑宽度是4，会占据 x,y - x+4,y+4 的矩形，需要避让
2. _find_nearest_empty_spot 只需要尝试一次，失败之后使用以前那种随机取点的方法，再尝试3次

> **Plan**
> 1. 添加 `import random`
> 2. 替换常量区：移除 MOVE_CITY_MAX_RETRIES/CITY_RADIUS/CITY_MIN_GAP，新增 _CITY_TYPES/_CITY_RADIUS/_STEAM_FACTORY_KEY/_STEAM_FACTORY_RECT/_OTHER_BUILDING_WIDTH/RANDOM_RETRY_COUNT/RANDOM_RETRY_RADIUS
> 3. 修改 `_find_empty_spot`：障碍物从 set[tuple[int,int]] 改为 list[tuple[int,int,int,int]] 矩形，按建筑类型计算不同尺寸；is_blocked 改为 AABB 矩形重叠检测
> 4. 重写 `_retry_move_city`：1次智能搜索 + 3次随机偏移（±15格）

**Files:** `src/executor/l0_executor.py`

### 3. 确认建筑宽度

> **Q:** 建筑实际占据的是 4 格 (x ~ x+3) 还是 5 格 (x ~ x+4)？

4格 (x ~ x+3)

**Files:** `src/executor/l0_executor.py`

### 4. 确认随机重试半径

> **Q:** 随机重试的偏移半径 RANDOM_RETRY_RADIUS 你希望设为多少？

15

**Files:** `src/executor/l0_executor.py`
