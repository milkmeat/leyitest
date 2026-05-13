# Prompt Record

- Date: 2026-05-13
- Branch: master
- Commit: feat: 添加 create_ava skill（创建/加入 AVA 战场）

---

### 1

调用 cli 创建一个 ava战场，id=29999，持续24小时

> **Insight**
> 命令解析逻辑在 `src/main.py:2285-2289`，`extra` 参数通过 `duration=` 前缀识别时长，其余参数作为 `event_id`。默认时长 2 小时，传入 `duration=24` 覆盖为 24 小时；`begin_time` 取当前时间戳，`end_time` = now + 24×3600。GM 指令使用固定 uid `20010643` 作为请求头身份。

### 2

/document-skills:skill-creator 创建一个skill "frozen_island:create_ava"，用上面的方法创建ava战场，如果用户没有说明持续时间，向用户询问（有一个默认选项是24hour）

> **Insight**
> Skill 发现机制: Claude Code 会扫描 `.claude/skills/*/SKILL.md`（一级子目录）来发现项目级 skills，扁平结构是必须的。触发机制: `description` 字段是触发匹配的核心——Claude 根据 description 决定何时使用该 skill。`AskUserQuestion` 是 Claude Code 内置的交互工具，支持选项列表。

**Files:** `.claude/skills/create_ava/SKILL.md`

### 3

将20010643加入ava=29999

**Files:** (CLI 命令执行，无文件变更)

### 4

在这个skill中， "加入ava战场"要同时做两个操作: 1 将其加入ava战场名单 2将其移入ava战场

> **Insight**
> 原子操作设计: "加入战场"被拆成 `uid_ava_add`（加名单）→ `uid_ava_enter`（移入）两步串联，Step 1 失败则不执行 Step 2，避免产生"在名单中但未进入"的中间状态。触发词扩展: description 新增了"加入"、"移入"、"进入"、"add"、"join"等关键词。

**Files:** `.claude/skills/create_ava/SKILL.md`

### 5

将20010643加入ava=29999

**Files:** (CLI 命令执行，无文件变更)
