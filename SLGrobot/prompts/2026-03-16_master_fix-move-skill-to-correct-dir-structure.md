# Prompt Record

- Date: 2026-03-16 11:38
- Branch: master
- Commit: fix: move custom skill to correct directory structure for Claude Code loading

---

### 1. Ask about add-screenshot-test skill visibility

你能看到 add-screenshot-test 这个skill吗

> **Insight**
> Claude Code 的 skill 系统需要在特定配置中注册才会被识别。仅仅把 `.md` 文件放在 `.claude/skills/` 目录下，不一定会自动变成可调用的 skill。系统当前加载的 5 个 skills（simplify、claude-api、planning-with-files、commit-with-prompts、recap）可能是通过 settings 或其他机制注册的。

### 2. Ask how to fix skill loading

怎么让他被正确加载

> **Insight**
> Claude Code 的 skill 加载机制扫描 `.claude/skills/` 下的子目录，每个子目录代表一个 skill，入口文件固定为 `SKILL.md`。当前已加载的 5 个 skills 来自插件市场（marketplace），通过 settings 中的 `enabledPlugins` 注册，走的是不同的加载路径。本地自定义 skill 只需目录结构正确，不需要额外在 settings 中注册，重启会话后自动生效。

**Files:** `.claude/skills/add-screenshot-test/SKILL.md`

### 3. Confirm the move operation

> **Q:** 要我帮你移动吗？执行 mkdir + mv 将 skill 文件移到正确的目录结构。

yes

> **Insight**
> 本地 skill 的加载是热生效的，不需要重启会话，目录结构正确后下一次工具调用时就会被扫描到。`SKILL.md` 中的第一个 `# 标题` 会被自动用作 skill 的显示名称。

**Files:** `.claude/skills/add-screenshot-test/SKILL.md`
