## 目标
在API接口中，对于普通地图，和ava(lvl)地图，存在两套命名相似，功能相似的命令字。
检查现有代码，看看cli是不是都实现了ava命令字的自动切换：当cli命令行带有参数--ava 时，切换到ava命令字。否则使用普通地图(test环境中 sid=1)命令字

## 任务
- 1. 补充l2_system_ava 的prompt，l2 决策环节可以自动切换到ava专用提示词，假设run或者l2_decide提供了--ava参数时。
- 2. sync命令读取地图信息时，根据--ava参数自动切换
- 3. 查询玩家信息时，打印出他当前在哪个地图，并自动切换命令字（即使--ava参数未提供）


## 工作项分解

### WI-1: get_player_info 显示当前地图并自动切换
- [x] cmd_get_player_info 中调用 get_player_lvl_info 检测玩家位置
- [x] 打印玩家当前在哪个地图（普通地图 / AVA lvl_id=xxx）
- [x] 即使未提供 --ava 参数也能自动检测

### WI-2: L2/L1 AVA prompt 自动切换
- [x] 创建 l2_system_ava.txt（基于 l2_system.txt + AVA 战场特有规则）
- [x] L2Commander.__init__ 接受 prompt_template 参数（与 L1Leader 一致）
- [x] cmd_l2_decide / cmd_run 在 --ava 时自动传入 ava 模板
- [x] l1_decide / run 在 --ava 时自动切换 L1 prompt（无需额外 --l1-prompt ava）
- [x] --l1-prompt 显式指定时仍然优先（覆盖自动切换）
- [x] 更新 CLI --help 信息

### WI-3: sync 单账号自动检测 AVA
- [x] sync <uid> 时自动调用 get_player_lvl_info 检测
- [x] 如果在 AVA 战场，打印提示并使用 AVA 命令字同步

## 要求
- 如有不明确的项目，一开始就向我询问，并更新本文件
- 都明确后，先分解成适当的工作项，更新本文件。开始开发调试
- 每个工作项进度完成后，更新本文件
- 所有新完成的命令字，都要在mock server上测试通过

## 验收标准
cli命令能正确相应，必要时自动切换