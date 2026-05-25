# Prompt Record

- Date: 2026-05-25 16:30
- Branch: master
- Commit: feat: defend.txt 增加积分态势/时间动态策略 + 弹性防守分配

---

### 1

比较一下 @src\ai\prompts\l2_ava\ 目录下， defend.txt与default.txt的区别，看看如何改进defend.txt

> **Insight**
> 这两个 prompt 是同一个 L2 指挥官模板的不同策略变体。`default.txt` 是"动态平衡"版本（根据积分动态切换攻防），`defend.txt` 是"防守优先"版本。对比它们的设计思路能看到 prompt engineering 中"策略参数化"的典型模式。

### 2

现在的代码有把剩余时间传进去吗

> **Insight**
> 这是 prompt 设计中常见的"数据传了但没指导"问题——模型能看到信息不等于会正确利用它。`default.txt` 通过"时间紧迫加权"规则明确指导 LLM 在末期如何行为，`defend.txt` 缺少这部分会导致 LLM 在比赛最后阶段仍按常规节奏行动。

### 3

好的，修改defend.txt

**Files:** `src/ai/prompts/l2_ava/defend.txt`
