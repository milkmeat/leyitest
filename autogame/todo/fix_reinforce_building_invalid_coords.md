## 目标
修复 LVL_REINFORCE_BUILDING 驻防失败、目标建筑坐标为 (0,0) 的问题（日志中出现 6 次）

## 背景
对战日志分析发现，`LVL_REINFORCE_BUILDING` 执行失败 6 次，
错误信息为："派出失败：1次移城+3次派兵重试，但目标建筑不在 (0,0)"。

这说明 L0 执行层在尝试驻防时，解析出的目标建筑坐标为 (0,0)，属于无效坐标。

## 根因分析
- L1 prompt 告诉 AI `target_x/target_y` 对 REINFORCE 是可选的（API 用 `pos="nil"` 按 building_id 定位）
- L0 验证只检查 `building_id` 非空，不要求坐标
- L0 预处理 `_preprocess_lvl_attack_building` 用 `instr.target_x/target_y`（即 0,0）做距离计算
- 距离 = hypot(0-cx, 0-cy) 通常 > 20，触发 `LVL_MOVE_CITY` 转换，目标 (0,0)，移城失败
- 坐标从 building_id 解析的逻辑只存在于 INITIATE_RALLY，REINFORCE 没有
- JOIN→REINFORCE 转换也不设置坐标，同样产生 (0,0) 问题

## 任务
- [x] 1. 检查 L1 输出中 REINFORCE_BUILDING 指令的 building_id 和坐标字段
- [x] 2. 检查 L0 executor 中 REINFORCE_BUILDING 的坐标解析逻辑
- [x] 3. Fix 1: 在 `_preprocess_lvl_attack_building` 中添加坐标补全（从 buildings 缓存解析）
- [x] 4. Fix 2: 距离检查中增加 (0,0) 安全网（跳过移城转换，直接放行）
- [x] 5. 回归测试：10 loop 模拟，REINFORCE→MOVE_CITY 转换 = 0

## 修复结果
- **REINFORCE→MOVE_CITY 转换: 0 次**（修复前大量出现）
- 剩余 REINFORCE 失败全部是 `queueid=6001 has occupied`（队列占用，独立问题，见 fix_queue_occupied_awareness.md）
- 修改文件: `src/executor/l0_executor.py`（`_preprocess_lvl_attack_building` 函数）

## 状态: ✅ 已完成
