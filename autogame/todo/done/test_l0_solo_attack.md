## 目标
在test环境测试 账号A对账号B 发动攻击（solo）
生成一个test_solo.sh，可以打印出详细的测试项目和运行结果

## 任务
- 使用 A=20010366, B=20010373 进行测试
测试流程如下
- 先给A,B都加上足够的宝石
- 给A,B都加上随机数量的士兵，记录士兵初始数量
- B移城到一随机位置
- 打印出B的位置，等待1分钟（我可以人工在模拟器上观察B是否移城成功）
- A移城到B的旁边
- A对B发起侦察（scout_player），只需要发起动作，不需要读取侦察结果
- A对B发起攻击(attack_player)
- 等待1分钟
- 验证A,B的士兵数量都减少了



## 实现方式
所有测试动作通过 CLI 文本指令触发（`python src/main.py <command> <args>`），不直接调用 Python 函数。

示例:
```bash
python src/main.py add_gem 20010366 77777       # GM 设置宝石
python src/main.py get_gem 20010366              # 查询宝石数量
python src/main.py l0 MOVE_CITY 20010366 500 500 # L0 执行器移城
python src/main.py get_player_pos 20010366       # 查询坐标
```

## 要求
- ~~如有不明确的项目，一开始就向我询问，并更新本文件~~ ✅ 已确认
- ~~都明确后，先分解成适当的工作项，更新本文件。开始开发调试~~ ✅ 见下方工作项
- ~~每个工作项进度完成后，更新本文件~~ ✅
- ~~所有新完成的命令字，都要在mock server上测试通过~~ ✅

## 验收标准
测试脚本会判断比较所有测试项目是否通过，打印PASS/FAIL的个数
测试项目必须有意义并全部PASS

## 工作项分解

### 1. Mock 数据准备 ✅
- 在 `mock_data.yaml` 中添加 uid=20010373 (B账号) 测试数据

### 2. attack_player CLI 命令增强 ✅
- `src/main.py` 的 `attack_player` 命令新增可选参数 `[soldier_id count]`
- march_info 格式按服务器要求组装（含 hero, carry_lord, leader, queue_id, soldier_total_num 等）

### 3. 编写 bash 测试脚本 ✅
- `test_solo.sh`: 纯 bash 脚本，9 步完整测试流程
- Mock 模式跳过 sleep 等待和士兵减少验证 (SKIP)
- B 移城和 A 移城均带重试逻辑（坐标可能被占用）
- 攻击/侦察使用 B 的实际坐标（而非移城目标值）

### 4. Mock 环境测试 ✅
- 10/10 PASS, 0 FAIL, 2 SKIP (士兵减少验证在 mock 下 SKIP)

### 5. Test 环境测试 ✅
- 12/12 PASS, 0 FAIL, 0 SKIP

## 测试项目清单

| # | 测试名称 | CLI 指令 | 验证方式 | Mock | Test |
|---|---------|---------|---------|------|------|
| 1 | A 宝石设置 | `add_gem A 200000` | get_gem 读回 == 200000 | ✅ | ✅ |
| 2 | B 宝石设置 | `add_gem B 200000` | get_gem 读回 == 200000 | ✅ | ✅ |
| 3 | A 士兵添加 | `add_soldiers A 204 RAND` | get_soldiers 读回 == old+RAND | ✅ | ✅ |
| 4 | B 士兵添加 | `add_soldiers B 204 RAND` | get_soldiers 读回 == old+RAND | ✅ | ✅ |
| 5 | B 移城命令执行 | `l0 MOVE_CITY B x y` | 输出包含 [OK]（带重试） | ✅ | ✅ |
| 6 | B 移城坐标验证 | `get_player_pos B` | 坐标 == (x,y) | ✅ | ✅ |
| 7 | A 移城命令执行 | `l0 MOVE_CITY A x+3 y` | 输出包含 [OK]（带重试多偏移） | ✅ | ✅ |
| 8 | A 移城坐标验证 | `get_player_pos A` | 坐标 == (x+offset,y) | ✅ | ✅ |
| 9 | A 侦察 B | `scout_player A B x y` | 命令执行成功 | ✅ | ✅ |
| 10 | A 攻击 B | `attack_player A B x y 204 5000` | 命令执行成功 | ✅ | ✅ |
| 11 | A 士兵减少验证 | `get_soldiers A 204` | 攻击后 < 攻击前 | SKIP | ✅ |
| 12 | B 士兵减少验证 | `get_soldiers B 204` | 攻击后 < 攻击前 | SKIP | ✅ |

## 关键发现

1. **主城占位宽度**: 主城在地图上占多格，移城到相邻玩家旁边时偏移 +1 不够，需要 +3 以上。脚本使用多偏移重试 (±3, ±5, ±7...)
2. **移城坐标冲突**: test 环境有大量账号，随机坐标也可能被占用 (ret_code=21104/21105)，B 移城也需要重试
3. **dispatch_troop march_info 格式**: 必须包含完整字段（hero, carry_lord, leader, soldier_total_num, heros, queue_id, soldier），缺少任何字段均返回 ret_code=30114
4. **实际坐标 vs 目标坐标**: 移城可能失败，后续操作（侦察/攻击）必须使用实际坐标而非移城目标值
