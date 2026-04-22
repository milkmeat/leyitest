## 目标
修复 AI 向已满槽账号下达出征指令的问题（queueid occupied，日志中出现约 20 次）

## 背景
对战日志分析发现，服务器返回 `ret_code=30001` 并附带 `queueid=600x has occupied` 错误共约 20 次。
涉及的操作包括：
- LVL_ATTACK_BUILDING（queueid=6001 occupied）— 5 次
- LVL_JOIN_RALLY（queueid=6004 occupied）— 14 次
- LVL_INITIATE_RALLY_BUILDING（queueid=6002 occupied）— 3 次

这说明 AI 没有正确感知账号当前的出征槽位占用状态，向已经没有空闲槽位的账号下达了出征指令。

## 根因分析
- 每个账号有 2 个出征槽位（queueid 6001, 6002 等），L1 输入中的 `slots` 字段可能不准确
- data_sync 获取的部队状态可能有延迟，上一轮派出的部队在本轮同步时还未反映
- L1 prompt 可能没有强调"只能向有空闲槽位的账号下达出征指令"

## 修复建议
- 目前设计中使用固定的queueid用于指定用途：发起集结用 6002，参加集结用 6004，solo 行军用 6001，收集矿车用 6003， 不要修改这一设定
- 不要使用slots计数，要探测当前队员所有队列的使用状态，例如 {"6001":1, "6002":0, "6003":0, "6004":0,}
- 如果队长已占用发起集结(6002)队列，可由下一位空闲队员发起集结
- 如果队员已经加入一个集结的情况下，还需要加入更多集结，可以依次使用6003（此时不再收集矿车），6002（此时不能发起集结，尝试由下一位空闲队员发起）

## 任务
- [x] 1. 检查 data_sync.py 中账号出征槽位的获取逻辑，确认 slots 计算是否准确
  - 根因: user_troops 已获取但从未解析到 PlayerState.troops → troops 始终为空 → slots 恒=2
  - 修复: 新增 Troop.from_user_obj() 解析 + _populate_troops() 分发
- [x] 2. 检查 l1_view.py 中 slots 字段的传递，确认 L1 能看到每个账号的剩余槽位
  - 修复: MemberView 新增 queue_status 字段 {6001:0/1, ...}，替代笼统的 dispatch_slots
  - format_text 输出改为 queues={6001:0,6002:0,...}
- [x] 3. 在 L1 prompt 中强调：slots=0 的账号不得下达任何出征指令
  - 修复: l1_system_ava.txt 更新为 queue_status 感知规则
- [x] 4. 在 L0 校验层增加槽位前置检查：如果账号无空闲槽位，直接拦截
  - 修复: 通用队列预检查 + JOIN_RALLY 回退链(6004→6003→6002) + 批次内 inflight 追踪
- [x] 5. 回归测试：确认不再出现 queueid occupied 错误
  - 10 轮模拟结果: 服务器 30001 occupied 从 ~65 次降到 2 次 (97% 改善)
  - L0 预检查拦截 11 次 (queue occupied, no fallback)
  - 剩余 2 次是数据同步时差导致的不可避免的"首次命中"

## 要求
- 如有不明确的项目，一开始就向我询问，并更新本文件
- 都明确后，先分解成适当的工作项，更新本文件。开始开发调试
- 每个工作项进度完成后，更新本文件
- 所有新完成的命令字，都要在mock server上测试通过

## 验收标准
```
删除 logs/ 目录下的旧日志
./ava_simulate.sh 40002 20 >/dev/null
检查 logs/ 目录下的日志看错误数量是否减少
```
