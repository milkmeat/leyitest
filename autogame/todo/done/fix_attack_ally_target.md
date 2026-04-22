## 目标
修复 AI 攻击友方目标的问题（服务器返回 ret_code=28003，日志中出现 20 次）

## 背景
对战日志分析发现，服务器返回 `ret_code=28003`（"The target is your ally"）共 20 次。
AI 把友方玩家或友方占领的建筑当成了敌方目标来攻击。

这是一个严重的逻辑错误——不仅浪费了行动机会，还说明 AI 的敌我识别存在缺陷。

## 根因分析
- L1 数据输入中建筑的 owner 信息可能不够明确（中立 vs 友方 vs 敌方）
- 建筑在上一轮被友方占领后，L1 的视图可能还是旧数据（中立状态）
- L1 prompt 可能没有强调"不得攻击友方目标"的约束
- **核心 gap**: Phase 1 sync 到 Phase 4 action 之间有 ~150s 的 L1/L2 思考时间，
  期间建筑归属可能变化，sync 缓存过时导致 L0 预检查无法拦截

## 任务
- [x] 1. 检查 l1_view.py 中建筑归属信息的构建逻辑，确认 owner 字段是否实时更新
  → 逻辑正确：用 alliance_id 对比 _my_alliance_id，每轮 sync 刷新
- [x] 2. 检查 data_sync.py 的建筑数据同步是否在每轮开始时刷新
  → 正确：每轮 Phase 1 通过 lvl_battle_login_get 获取最新建筑数据
- [x] 3. 在 L1 prompt 中增加明确约束：禁止攻击 owner=friendly 的建筑
  → l1_system_ava.txt 已有规则，增强措辞：明确禁止 INITIATE_RALLY 和 ATTACK 对 Ours 建筑
- [x] 4. 在 L0 校验层增加前置检查：如果目标是友方，直接拦截并跳过
  → 新增 Fix 6: _check_building_ownership_fresh() 实时查询服务器建筑归属
    - INITIATE_RALLY 前：缓存显示敌方时查询服务器，若实际已是我方则拦截
    - ATTACK_BUILDING 前：同上，自动转为 REINFORCE
- [x] 5. 回归测试：确认不再出现 ret_code=28003
  → ava_simulate.sh 20 完成：28003 错误 20→0（完全消除）
  → 20 轮日志，248 成功 / 80 失败，总成功率 76%
  → 剩余失败主要是 queue occupied SKIP（68 次），非本次修复范围

## 状态: ✅ 已完成 (2026-04-22)

## 修改的文件
- `src/executor/l0_executor.py` — 新增 `_check_building_ownership_fresh()` 方法 + Fix 6 集成
- `src/ai/prompts/l1_system_ava.txt` — 增强 Attack Method Selection Rules 第 2 条措辞

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
