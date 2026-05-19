# Prompt Record

- Date: 2026-05-19 11:00
- Branch: master
- Commit: fix: _find_empty_spot 移城空位算法修正（点碰撞+steam factory 强制注入）

---

### 1

看一下最新的ava simulate日志，账号在进攻 "steam factory" 时，尝试移城到 13900015900， 产生移城失败。这个格子被建筑本身占领了。建筑中心是(139,155)，请修改移城时选择空闲格子的算法。对于该建筑，空闲坐标有：138,159 ; 141,161; 145,159; 142,153； 编写恰当的单元测试验证通过

> **Insight**
> - 碰撞检测模型不匹配是根因：代码假设城市是 5×5 面积碰撞，但服务器只检查目标**点**是否在建筑占地内
> - Steam factory 是固定建筑，地图查询可能不返回它，必须硬编码注入
> - Rect 上界 (145,161) 比实际占地 (144,160) 大了 1 格（exclusive vs inclusive 混淆）

**Files:** `src/executor/l0_executor.py`, `tests/test_find_empty_spot.py`

### 2

日志如下。你继续分析
10:22:13 [src.executor.game_api] WARNING: [业务失败] cmd_name=lvl_move_city cmd=lvl_move_city uid=20010683 code=21105
Header: {"aid": 20000118, "battle_id": 0, "battle_type": 0, "castle_lv": 25, "chat_scene": ",kingdom_1", "did": "self-system", "invoker_name": "ying_test_debug", "ksid": 1, "lvl_id": 40001, "sid": 1, "uid": 20010683}
Param: {"use_gem": 1, "item_id": 1, "tar_pos": 13900015900}
Response: {"res_header": {"ret_code": 21105, "cost_time_us": 0, "ret_time_s": 1779157334, "err_msg": ""}, "request": {"header": {"aid": 20000118, "battle_id": 0, "battle_type": 0, "castle_lv": 25, "chat_scene": ",kingdom_1", "did": "self-system", "invoker_name": "ying_test_debug", "ksid": 1, "lvl_id": 40001, "sid": 1, "uid": 20010683}, "request": {"cmd": "lvl_move_city", "param": {"use_gem": 1, "item_id": 1, "tar_pos": 13900015900}}, "extra_info": {"no_checkac": 1, "op_cmd": 1}}, "res_data": []}
10:22:13 [src.executor.l0_executor] WARNING: L0 服务器返回错误: LVL_MOVE_CITY uid=20010683 —  (Please move your Haven to an open space.)

> **Insight**
> - 碰撞模型从 5×5 AABB 改为点在矩形内：匹配服务器实际行为，不再过度排除合法坐标
> - 固定建筑无条件注入：解决地图查询不返回特殊建筑的盲区问题
> - 螺旋步长从 2 改为 1：确保不跳过最近的空位（如距离 1 的边缘格子）

**Files:** `src/executor/l0_executor.py`, `tests/test_find_empty_spot.py`
