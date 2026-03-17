# Prompt Record

- Date: 2026-03-17 17:30
- Branch: master
- Commit: fix: auto-extract building target_type, add LLM 429 backoff, L1 live test

---

### 1. Review progress and plan next steps

看一下progress.md，做下一步计划

> **Insight**
> 项目进度文件显示了一个明确的开发梯度：Phase 1 的基础设施全部就绪，Phase 2 的 L1 决策核心已完成但缺少实战闭环验证。下一步的重点应该是打通端到端验证而非继续写新代码。

### 2. Proceed with recommended plan

就这样做

> **Q:** 你想从哪一步开始？最合理的路径是先做第1步 L0 ActionType 补全（代码量小，为实战测试扫清障碍），然后跑第2步 L1 实战测试。

> **Insight**
> L0 执行器已经完整支持全部 9 种 ActionType（包括 RALLY_DISMISS 和 RECALL_REINFORCE），progress.md 第87行的"待完成"实际上已经做完了。所以我们可以直接跳到第2步：L1 单小队实战测试。

> **Insight**
> 测试脚本覆盖了6个维度：LLM 连通性 → 单小队决策 → JSON 结构校验 → 3轮稳定性 → 主循环集成 → 4小队覆盖。这种递进式测试策略可以精确定位问题出在哪一层。

> **Insight**
> 测试暴露了两个核心问题：
> 1. LLM 超时 (30s) — L1 视图 prompt 可能过大导致 GLM 无法在 30s 内响应
> 2. 速率限制 (429) — 快速连续调用触发了智谱 API 的频率限制，且代码中没有退避重试机制
> 3. 测试脚本小bug — "跳过" 匹配到了 L2 stub 输出而非 L1

**Files:** `docs/progress.md`, `config/system.yaml`, `src/ai/llm_client.py`, `test_l1_live.sh`

### 3. Switch to GLM-4.5-Air model

我把模型换成了 GLM-4.5-Air ，继续测试

> **Insight**
> L1 决策引擎首次实战成功！LLM 为 Alpha 小队 5 个成员各分配了 ATTACK_TARGET 指令，目标是附近的中立建筑（按距离排序的 top 5）。这符合 L1 prompt 中"中立建筑→各自 solo 攻击"的规则。

> **Insight**
> 13/14 通过！关键问题：主循环执行 22 条指令，但 20 条失败 (ok=2, fail=20)——L0 执行时游戏服务器返回 30001 错误。

> **Insight**
> 发现了！attack_building 的 target_type: 13 标注为"待确认"。建筑 ID 格式是 {type}_{id}_{level}，服务器要求 target_type 与建筑实际类型一致。之前硬编码 target_type: 13 导致 20/22 条指令全部失败。这是一个协议层 bug。

> **Insight**
> Phase 2 实战验证的关键收获：
> 1. 协议层隐患暴露: target_type 硬编码 13 导致所有建筑攻击失败，这类 bug 在 dry-run 测试中完全不可见
> 2. LLM 模型选择很重要: GLM-4.7 在 60s 内超时，GLM-4.5-Air 在 49s 内响应
> 3. 速率限制是生产级系统的必考项: 4 组 L1 并行 = 4 个并发 LLM 调用，不加退避重试很容易触发 429

**Files:** `src/executor/game_api.py`, `src/executor/l0_executor.py`, `test_l1_live.sh`, `docs/progress.md`
