# Prompt Record

- Date: 2026-04-03 00:10
- Branch: master
- Commit: refactor: 改善 _apply_team_swap 可读性 + 标注 _team 全局变量技术债

---

### 1. Review commit 72dcf51 的 --team 变更

review 72dcf51 这个变更，看看有没有问题

> **Plan**
> 对 commit 72dcf51 进行 code review，检查了四个潜在问题：
> - P1: `_apply_team_swap` 中 print 行过长（三元表达式嵌套），确认逻辑正确但可读性差
> - P2: `--team` 无值时静默忽略（与 `--llm` 行为一致，低优先级）
> - P3: `_team` 模块级全局变量的线程安全隐患（当前单进程可接受，标记技术债）
> - P4: `load_all(alliance=...)` + `_apply_team_swap` 职责分离 — 验证 `load_all` 只切换 squads，swap 只交换 accounts/alliances，无冲突

> **Insight**
> 1. P1 修复: 将重复的 `config.accounts.alliances` 三元表达式提取为 `ally` 局部变量，消除了单行 120+ 字符的问题，逻辑不变
> 2. P3 标注: 在 `_team` 声明处添加 NOTE 注释，将来如果要支持双 team 并行控制时能快速定位需要重构的点

**Files:** `src/main.py`

### 2. 选择要修复的问题

> **Q:** 需要我修复这些小问题吗？(P1-P4)

只处理1,3

**Files:** `src/main.py`
