## 目标
修复 LVL_JOIN_RALLY 指令缺少 rally_id 的问题（日志中出现 52 次）

## 背景
对战日志分析发现，L1 AI 下达 `LVL_JOIN_RALLY` 指令时，经常不提供有效的 `rally_id`，
导致 L0 执行层直接校验失败，报错 "LVL_JOIN_RALLY 需要 rally_id 非空"。

这是出现次数最多的单一错误类型，占全部失败的 43%（52/120）。

另有 17 次 `LVL_JOIN_RALLY` 失败但错误信息为空，可能也与此相关。

## 根因分析
- L1 prompt 中可能没有明确要求 AI 输出 rally_id 字段
- 数据感知层（l1_view）可能没有把当前可加入的集结列表及其 rally_id 传递给 L1
- L0 校验层拦截了无效指令，但 L1 层面缺乏足够信息来生成正确指令

## 任务
- [x] 1. 检查 l1_view.py 是否在 L1 输入中包含了当前活跃集结的 rally_id 列表
  - 已确认：代码逻辑正确（ActiveRally 模型 + format_text），但 snapshot.rallies 始终为空（sync 时刻无集结）
- [x] 2. 检查 L1 prompt 模板，确认是否要求 AI 在 JOIN_RALLY 时必须指定 rally_id
  - 已修改：强化 prompt 要求每个小队自己发起集结，禁止跨小队 JOIN
- [x] 3. 在 L0 校验层增加更明确的错误提示（如果尚未有）
  - 已有：L0 校验 "LVL_JOIN_RALLY 需要 rally_id 非空" 已存在
- [x] 4. 修复 L1 数据输入，确保可加入的集结信息（含 rally_id）传递到 L1
  - 已加 debug 日志诊断 svr_lvl_rally_brief_objs 是否返回
  - 根因：sync 时刻（Phase 1）还没有集结，集结在 Phase 4 才发起
- [x] 5. 修复 L1 prompt，明确 JOIN_RALLY 必须携带 rally_id
  - 已修改：每个小队必须自己 INITIATE，rally_id 由系统自动回填
- [ ] 6. 回归测试：运行一轮完整对战，确认 JOIN_RALLY 不再因缺少 rally_id 失败

## 日志对比分析结论

### 成功模式（PhoenixRise2026_loop_9）
同一小队批次内 INITIATE 成功 → L0 提取 rally_id → 自动回填给后续 JOIN → 成功

### 失败模式 A：INITIATE 返回 28003（TestSquad2026_loop_7）
建筑已被我方占领 → INITIATE 失败 → 无 rally_id 可回填 → 整批 JOIN 级联失败

### 失败模式 B：跨小队 JOIN 无 INITIATE
L2 命令"加入其他小队集结" → 小队只有 JOIN 没有 INITIATE → 全部失败

### 关键发现
1. L1 从未输出过 rally_id（100% 为空）
2. "Active Rallies" 从未出现在 L1 输入中
3. 28003 = "The target is your ally"
4. 自动回填是唯一成功路径

## 实施的修复

### Fix 1: INITIATE 28003 恢复机制 ✅
- 文件: `src/executor/l0_executor.py`
- 当 INITIATE 返回 28003 时，查询目标上的活跃集结
- 找到 → 设置 last_rally_id 供后续 JOIN 回填
- 没找到 → 后续 JOIN 转为 REINFORCE

### Fix 2: 每个小队自己发起集结 ✅
- 文件: `src/executor/l0_executor.py`, `src/ai/prompts/l1_system_ava.txt`
- L1 prompt 强化：禁止跨小队 JOIN，每个小队必须自己 INITIATE
- L0 自动转换：无前置 INITIATE 的 JOIN → 自动转为 INITIATE（按坐标匹配建筑）

### Fix 3: Active Rallies 数据诊断 ✅
- 文件: `src/perception/data_sync.py`
- 加 debug 日志诊断 svr_lvl_rally_brief_objs 是否被服务器返回
- 根因：sync 时刻无集结数据是正常的（时序问题）

### Fix 4: L0 预检查建筑归属 ✅
- 文件: `src/executor/l0_executor.py`, `src/controller/loop.py`
- 将 buildings 传入 execute_batch
- INITIATE 前检查建筑是否已是我方 → 跳过 INITIATE，避免 28003

### Fix 5: JOIN_RALLY 坐标补全 ✅
- 文件: `src/executor/l0_executor.py`, `src/ai/prompts/l1_system_ava.txt`
- L1 prompt: target_x/target_y 改为 Required
- L0 兜底: JOIN_RALLY target=(0,0) 时从最近 INITIATE 目标推断坐标

## 首轮测试结果 (lvl_id=39998, 22 loops)
- rally_id 空失败: 52 → 16 (降幅 69%)
- JOIN 成功率: ~57% → 67.3%
- 剩余 16 个失败全部是 target=(0,0)，已由 Fix 5 修复

## 要求
- 如有不明确的项目，一开始就向我询问，并更新本文件
- 都明确后，先分解成适当的工作项，更新本文件。开始开发调试
- 每个工作项进度完成后，更新本文件
- 所有新完成的命令字，都要在mock server上测试通过

## 验收标准
```
python main.py run --alliance TestSquad2026
# 运行至少 5 个 loop，LVL_JOIN_RALLY 不再出现 "rally_id 非空" 错误
# 日志中 JOIN_RALLY 的 success 率应 > 90%
```
