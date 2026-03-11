## 目标
在test环境测试通过仅作用与单一账号的L0命令。
生成一个test_l0.sh，可以打印出详细的测试项目和运行结果

## 任务
- 使用 uid=20010366 进行测试
- 测试方法是1.先读取账号状态，2.发起修改命令，3.再读取账号最新状态，4.验证状态的变化符合预期
- 测试范围：add_gem， add_soldiers, add_resource, move_city
- add_gem 是SET动作（实测确认），直接设置宝石数为指定值
- add_soldiers 是ADD动作（实测确认），在原兵力数量上增加指定数量
- add_resource 是批量资源操作，验证命令执行成功 (ret_code=0)
- move_city 是移城动作，随机生成目标坐标，验证坐标变更。需要有足够宝石，且目标坐标不能被占用

> **注意**: 原始描述中 add_gem/add_soldiers 的 ADD/SET 行为描述与实测相反，已按实测修正。

## 要求
- ~~如有不明确的项目，一开始就向我询问，并更新本文件~~ ✅ 已确认
- ~~都明确后，先分解成适当的工作项，更新本文件。开始开发调试~~ ✅ 见下方工作项
- ~~每个工作项进度完成后，更新本文件~~ ✅
- ~~所有新完成的命令字，都要在mock server上测试通过~~ ✅

## 验收标准
测试脚本会判断比较所有测试项目是否通过，打印PASS/FAIL的个数
测试项目必须有意义并全部PASS

## 实现方式
所有测试动作通过 CLI 文本指令触发（`python src/main.py <command> <args>`），不直接调用 Python 函数。

示例:
```bash
python src/main.py add_gem 20010366 77777       # GM 设置宝石
python src/main.py get_gem 20010366              # 查询宝石数量
python src/main.py l0 MOVE_CITY 20010366 500 500 # L0 执行器移城
python src/main.py get_player_pos 20010366       # 查询坐标
```

## 工作项分解

### 1. Mock Server 行为修正 ✅
- `handle_op_self_set_gem`: SET 行为（`player["gem"] = gem_num`）
- `handle_op_add_soldiers`: ADD 行为（`s["value"] += soldier_num`）
- `handle_login_get`: 新增 `svr_gem_stat` 模块支持

### 2. Mock 数据准备 ✅
- 在 `mock_data.yaml` 中添加 uid=20010366 测试账号

### 3. CLI 查询命令扩展 ✅
- `src/main.py` 新增 `get_gem <uid>` — 输出纯宝石数字
- `src/main.py` 新增 `get_soldiers <uid> <soldier_id>` — 输出纯兵种数量

### 4. 编写 bash 测试脚本 ✅
- `test_l0.sh`: 纯 bash 脚本，通过 CLI 文本指令触发测试

### 5. 测试通过 ✅
- Mock 环境: 6/6 PASS
- Test 环境: 6/6 PASS

## 测试项目清单

| # | 测试名称 | CLI 指令 | 验证方式 | Mock | Test |
|---|---------|---------|---------|------|------|
| 1 | add_gem SET 值验证 | `add_gem <uid> 77777` | get_gem 读回 == 77777 | ✅ | ✅ |
| 2 | add_gem SET 二次验证 | `add_gem <uid> 66666` | get_gem 读回 == 66666 (非ADD) | ✅ | ✅ |
| 3 | add_soldiers ADD 值验证 | `add_soldiers <uid> 204 500` | get_soldiers 读回 == old+500 | ✅ | ✅ |
| 4 | add_resource 命令执行 | `add_resource <uid> 0` | 输出包含"成功" | ✅ | ✅ |
| 5 | l0 MOVE_CITY 命令执行 | `l0 MOVE_CITY <uid> x y` | 输出包含 [OK] | ✅ | ✅ |
| 6 | l0 MOVE_CITY 坐标验证 | `get_player_pos <uid>` | 读回坐标 == (x,y) | ✅ | ✅ |

## 关键发现

1. **宝石读取**: `game_server_login_get` 不返回 `svr_gem_stat`，需要通过 `login_get` 并指定 `list=["svr_gem_stat"]` 获取
2. **move_city 约束**: 移城消耗宝石（不足返回 ret_code=20009），目标坐标被占用返回 ret_code=21105
3. **bash UID 变量冲突**: `UID` 是 bash 内置只读变量，脚本中需使用 `TEST_UID`
4. **命令行为与命令名对应**: `op_self_set_gem` = SET，`op_add_soldiers` = ADD（与命令名一致，但与原始任务描述相反）
