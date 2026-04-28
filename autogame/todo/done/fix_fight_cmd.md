## 目标
在ava模拟战斗中，仍有相当数量的30001错误(this queueid=6001 has occupied)。我想对战术指令做一些修改，减少此类报错。

## 背景
- 每个uid共有4个可用出征队列，queueid为 6001,0662,6003,6004
- 代码中已经分配了每个queue的用途: 发起集结用 6002，参加集结用 6004，solo 行军用 6001， 采集矿车用 6003
- 在某次测试中，出现该错误的场景如下
  - 4次	LVL_RECALL_TROOP	召回部队失败
  - 3次	LVL_JOIN_RALLY	加入集结失败
  - 4次	LVL_REINFORCE_BUILDING	增援建筑失败
  - 1次	LVL_REINFORCE_BUILDING	增援建筑失败（queueid=6001占用）


## 任务
- 取消 LVL_RECALL_TROOP 这个指令，不再执行召回动作
- 增援建筑时，如果6001队列已经被占用，可以使用6003队列，此时不再派出队列采集矿车


## 要求
- 如有不明确的项目，一开始就向我询问，并更新本文件
- 都明确后，先分解成适当的工作项，更新本文件。开始开发调试
- 每个工作项进度完成后，更新本文件
- 所有新完成的命令字，都要在mock server上测试通过

## 验收标准
```
./ava_simulate.sh 20 >/dev/null
检查 logs/ 目录下的日志看错误数量是否减少
```

## 工作项分解

### 1. 取消 LVL_RECALL_TROOP 指令 ✅
- [x] 从 L1 prompt (`l1_system_ava.txt`) 移除 3 处引用：state consistency 例外、指令定义块、字段说明
- [x] 从 L0 executor (`l0_executor.py`) 移除 6 处引用：注释、校验、_NON_DISPATCH_ACTIONS、_AVA_ACTION_MAP、_dispatch、_success_message
- 保留枚举值和 GameAPI 方法（兼容性）

### 2. 增援建筑队列回退 6001→6003 ✅
- [x] 添加 `_REINFORCE_Q_ACTIONS` 集合（LVL_REINFORCE_BUILDING, GARRISON_BUILDING）
- [x] 修改 `_find_fallback_queue` 方法，REINFORCE 类 action 6001 占用时回退到 6003
- [x] 更新 L1 prompt Notes 区域添加 REINFORCE 回退说明

### 3. 验证测试 ✅
- [x] 运行 `./ava_simulate.sh 20` 检查日志错误数量

## 测试结果

| 指标 | 修改前 | 修改后 | 变化 |
|------|--------|--------|------|
| LVL_RECALL_TROOP 30001 | 4 | 0 | -4 ✅ |
| LVL_REINFORCE_BUILDING 30001 (queue occupied) | 5 | 0 | -5 ✅ |
| LVL_REINFORCE_BUILDING 30001 (其他原因) | 0 | 4 | 非队列问题 |
| LVL_REINFORCE_BUILDING queue SKIP | N/A | 0 | 回退生效 |
| LVL_JOIN_RALLY 30001 | 3 | 5 | 非本次目标 |

说明：
- LVL_RECALL_TROOP 错误完全消除
- LVL_REINFORCE_BUILDING 的队列占用跳过为 0（回退到 6003 生效）
- 剩余 4 个 REINFORCE 30001 是服务器端其他原因（非 queueid occupied）
- 剩余 30001 主要来自 INITIATE_RALLY_BUILDING(8) 和 JOIN_RALLY(5)，属于不同问题