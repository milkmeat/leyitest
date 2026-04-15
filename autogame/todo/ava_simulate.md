## 目标
编写测试脚本，模拟一场ava战斗，持续一小时（参数可变），并打印出两个联盟各自的积分

## 任务
- 完成脚本 ava_simulate.sh，使用cli命令行完成全部操作。脚本需要打印出所有实际执行的cli命令
- 脚本使用方式为 `./ava_simulate.sh <ava_id> [duration_minutes]`，例如: `./ava_simulate.sh 29999` (默认60分钟) 或 `./ava_simulate.sh 29999 30`
- 脚本完成以下功能
  - 创建 ava 战场: 直接调用 `uid_ava_create <lvl_id>`，已存在时根据返回错误码判断并忽略
  - 将双方账号先退出到普通地图: `uid_ava_leave_all <lvl_id>` (已内置容错，不在战场的账号自动跳过)
  - 将双方账号加入到指定ava战场: `uid_ava_join_all <lvl_id>` (自动读取 accounts.yaml 分配 camp)
  - 为每个账号(双方)加上 10,000,000 宝石 (`add_gem <uid> 10000000`) 和三个兵种各 1,000,000 士兵:
    - `add_soldiers <uid> 4 1000000` (cavalry 骑兵)
    - `add_soldiers <uid> 104 1000000` (infantry 步兵)
    - `add_soldiers <uid> 204 1000000` (archer 弓兵)
  - 记录该战场的双方得分快照作为计分起点: `get_ava_score <uid> <lvl_id>` (由于战场会重复使用，起点不一定为0)
  - 并发启动两个后台进程:
    - `python src/main.py run --ava <ava_id> --team 1`
    - `python src/main.py run --ava <ava_id> --team 2`
  - 使用 `trap` 注册信号处理，确保脚本退出时(含 Ctrl+C)杀掉两个后台进程
  - `sleep <duration>` 等待对战时长结束后，kill 两个后台进程
  - 记录双方的得分快照作为计分终点
  - 将所有账号退出到普通地图: `uid_ava_leave_all <lvl_id>`
  - 打印本次对战双方各自的得分（计分终点 - 计分起点）


## 工作项

- [x] 编写 ava_simulate.sh 脚本（配置区 + 辅助函数 + 11步流程）
- [ ] 实际运行测试（`./ava_simulate.sh 29999 1` 快速验证）
- [ ] 修复运行中发现的问题
- [ ] 完整时长测试（`./ava_simulate.sh 29999 60`）

## 要求
- 如有不明确的项目，一开始就向我询问，并更新本文件
- 都明确后，先分解成适当的工作项，更新本文件。开始开发调试
- 每个工作项进度完成后，更新本文件
- 所有新完成的命令字，都要在mock server上测试通过

## 验收标准
```
./ava_simulate.sh 29999
# 默认持续运行60分钟，并打印出双方实际得分

./ava_simulate.sh 29999 30
# 持续运行30分钟
```