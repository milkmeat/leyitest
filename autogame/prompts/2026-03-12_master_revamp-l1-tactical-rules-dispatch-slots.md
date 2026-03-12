# Prompt Record

- Date: 2026-03-12 20:00
- Branch: master
- Commit: revamp L1 tactical rules: 2 dispatch slots with hero exclusivity

---

### 1. 重写部队派遣规则

把战术策略改一下，不要强调最多3只部队。新的规则如下：
1. 最多向城外派出2只部队，一只solo，一只rally(队长或队员)
2. rally的队长需要派出最强的英雄，且不再进行solo
3. rally的队员不需要派出英雄，需要派出指定的兵种参战
4. solo的时候需要派出最强的英雄
5. rally的队员因最强英雄未被占用，仍然可以solo别人
6. 派出的部队都有出征上限。未行动的部队会留在主城内进入防守状态，不需要另外下指令。

> **Insight**
> 新规则的核心变化是从"3部队自由调度"变为"最多2部队外出 + 角色区分"：Rally队长派最强英雄，占用1个出征槽位，不再solo；Rally队员派指定兵种（无需英雄），最强英雄空闲所以仍可solo；Solo玩家派最强英雄。未出征部队自动守城，不需要额外指令。LLM需要理解"英雄占用"的概念来做正确决策。

**Files:** `src/ai/prompts/l1_system.txt`, `src/perception/l1_view.py`, `CLAUDE.md`

### 2. 纠正纯Solo出征数

"纯Solo = 最多2支出征" 这个说法不对，因为最强英雄被占用，只能solo一只

> **Insight**
> Rally队员其实是出征效率最高的角色——因为加入集结不需要英雄，英雄空闲就能同时Solo，一个账号可以打出2支部队。相比之下，Rally队长和纯Solo都因为英雄占用只能出1支。这意味着L1在分配角色时，应该尽量让更多账号当队员而非队长。

**Files:** `src/ai/prompts/l1_system.txt`
