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

## 任务
- [ ] 1. 检查 data_sync.py 中账号出征槽位的获取逻辑，确认 slots 计算是否准确
- [ ] 2. 检查 l1_view.py 中 slots 字段的传递，确认 L1 能看到每个账号的剩余槽位
- [ ] 3. 在 L1 prompt 中强调：slots=0 的账号不得下达任何出征指令
- [ ] 4. 在 L0 校验层增加槽位前置检查：如果账号无空闲槽位，直接拦截
- [ ] 5. 回归测试：确认不再出现 queueid occupied 错误

## 要求
- 如有不明确的项目，一开始就向我询问，并更新本文件
- 都明确后，先分解成适当的工作项，更新本文件。开始开发调试
- 每个工作项进度完成后，更新本文件
- 所有新完成的命令字，都要在mock server上测试通过

## 验收标准
```
python main.py run --alliance TestSquad2026
# 运行至少 5 个 loop，不再出现 ret_code=30001 / queueid occupied 错误
```
