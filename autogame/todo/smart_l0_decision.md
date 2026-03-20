

## 目标
l0 executor增加一些智能判断逻辑，完全用python实现，不走llm


## 任务
- 当接收到 lvl_attack_building 并不是无条件派出军队进攻，而是做以下判断
- 判断当前主城坐标与目标建筑距离，如果欧式距离大于20的话，转换成lvl_move_city命令，移城到建筑附近的空位上
- 判断是否已有行军队列驻扎在建筑上，如有，什么都不做(最多只派出一只军队参与进攻)
- 以上条件都通过时，才真正执行lvl_attack_building


## 工作项

### 1. [已完成] _preprocess_lvl_attack_building 预处理方法
- 在 `L0Executor` 中新增 `_preprocess_lvl_attack_building()` 方法
- 部队去重：检查 `acct.troops` 中是否有部队 (MARCHING/STATIONED/FIGHTING/GARRISON) 目标为该建筑，有则跳过
- 距离检查：计算主城与目标的欧式距离，>20 格则转换为 `LVL_MOVE_CITY`（偏移 ±2 避免重叠）
- 文件：`src/executor/l0_executor.py`

### 2. [已完成] execute_batch 集成预处理
- 在 `execute_batch()` 循环中，对 `LVL_ATTACK_BUILDING` 指令调用预处理
- 预处理返回 `None` 时跳过（已有部队），返回新指令时替换（移城）
- 文件：`src/executor/l0_executor.py`

### 3. [已完成] cmd_l0 CLI 加载玩家状态
- CLI 的 `cmd_l0()` 改用 `execute_batch()` 替代 `execute()`
- 执行前通过 `get_player_info` 拉取玩家状态（城市坐标、部队列表），供预处理使用
- 文件：`src/main.py`

### 4. [已完成] --soldier 手动指定兵种/数量
- `AIInstruction` 新增 `soldier_id`、`soldier_count` 字段（默认 0=自动）
- `_build_march_info` 支持手动覆盖兵种/数量（仍受 DEFAULT_MARCH_SIZE 上限）
- `_parse_l0_shorthand` 统一解析 `--soldier <id> <count>` 参数
- 文件：`src/executor/l0_executor.py`、`src/main.py`


## 要求
- 如有不明确的项目，一开始就向我询问，并更新本文件
- 都明确后，先分解成适当的工作项，更新本文件。开始开发调试
- 每个工作项进度完成后，更新本文件
- 所有新完成的命令字，都要在mock server上测试通过

## 验收标准
我自己使用cli命令观察其行为

## 当前状态
**全部完成** — 所有工作项已实现并通过测试。

CLI 用法示例：
```bash
# 自动兵种，含 Smart L0 预处理（距离检查 + 部队去重）
python -m src.main l0 LVL_ATTACK_BUILDING <uid> <bid> <x> <y>

# 手动指定弓兵 3000
python -m src.main l0 LVL_ATTACK_BUILDING <uid> <bid> <x> <y> --soldier 204 3000
```