## 目标
为cli增加 --team <1|2> 参数，用于指定是管理我方还是敌方(1=accounts 我方；2=enemies 敌方)(默认为1)。这样我可以用cli轮流驱动team 1和team 2进行对战

## 任务
- [x] 1. 可以通过team参数来指定是管理我方(1)还是敌方(2)账号。默认为1
- [x] 2. team 1 对应accounts.yaml中的我方（accounts），team 2 对应 enemies
- [x] 3. 在ava战场中， team 对应 <camp_id> 字段， 1 代表我方， 2代表敌方
- [x] 4. 在 run 命令中， 管理指定的team，获取其对应的status，并为其输出命令
- [x] 5. 其他命令只要没有指定uid的，都应该支持team参数（sync, l0, l1_decide, l2_decide, l1_view, uid_helper 系列）

## 实现方案: Config Swap
- 在 `_load_config()` 中，当 team=2 时:
  - 交换 `accounts.accounts` ↔ `accounts.enemies`
  - 交换 `accounts.alliances.ours` ↔ `accounts.alliances.enemy`
  - 通过 `load_all(alliance="enemy")` 设置活跃小队为敌方
- 所有下游代码（DataSyncer, AIController, L0Executor, L1/L2）通过 `active_uids()`/`alliances.ours` 等访问器间接获取数据，**零改动**

## 修改文件
- `src/main.py` (唯一修改的文件)
  - 添加 `_team` 模块变量
  - `main()` 解析 `--team <1|2>` 全局参数
  - 添加 `_apply_team_swap()` 配置交换函数
  - 修改 `_load_config()` 支持 team 参数传递和交换
  - 迁移 6 处直接 `load_all()` 调用为 `_load_config()`
  - 更新帮助文本

## 要求
- [x] 如有不明确的项目，一开始就向我询问，并更新本文件
- [x] 都明确后，先分解成适当的工作项，更新本文件。开始开发调试
- [x] 每个工作项进度完成后，更新本文件
- [x] 所有新完成的命令字，都要在mock server上测试通过

## 验收标准
```
# 为我方输出一轮行动
python main.py run --once --team 1

# 为敌方输出一轮行动
python main.py run --once --team 2
```

## 验证结果
- `--team 1` (默认): 同步 uid 20010643-20010652, squads=[Alpha, Bravo], lvl_aid=1
- `--team 2`: 同步 uid 20010668-20010677, squads=[Red-A, Red-B], lvl_aid=2
- `--team 3`: 正确报错 "必须为 1 或 2"
- 参数顺序无关: `--team 2 --mock` 和 `--mock --team 2` 均可
