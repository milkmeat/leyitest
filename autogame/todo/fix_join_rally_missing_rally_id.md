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
- [ ] 1. 检查 l1_view.py 是否在 L1 输入中包含了当前活跃集结的 rally_id 列表
- [ ] 2. 检查 L1 prompt 模板，确认是否要求 AI 在 JOIN_RALLY 时必须指定 rally_id
- [ ] 3. 在 L0 校验层增加更明确的错误提示（如果尚未有）
- [ ] 4. 修复 L1 数据输入，确保可加入的集结信息（含 rally_id）传递到 L1
- [ ] 5. 修复 L1 prompt，明确 JOIN_RALLY 必须携带 rally_id
- [ ] 6. 回归测试：运行一轮完整对战，确认 JOIN_RALLY 不再因缺少 rally_id 失败

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
