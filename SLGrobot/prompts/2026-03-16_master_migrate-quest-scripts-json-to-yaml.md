# Prompt Record

- Date: 2026-03-16 17:45
- Branch: master
- Commit: feat: migrate quest scripts from JSON to unified YAML ScriptRunner

---

### 1. Migration plan implementation request

Implement the following plan: [detailed migration plan with 7 sections covering Context, Design Decisions, YAML format, modification file list, test updates, doc updates, and verification plan]

> **Plan**
> # 迁移方案：Quest Script (JSON) → YAML Script，移除 QuestScriptRunner
>
> ## Context
> 项目中存在两个脚本系统：QuestScriptRunner (JSON, 727行) 和 ScriptRunner (YAML, 481行)。目标：增强 ScriptRunner 覆盖全部功能，迁移 westgame2 的 6 个 quest script 为 YAML，更新集成点，删除 QuestScriptRunner。一次性切换。
>
> ## 设计决策
> 1. 统一 target 字段 — text/icon 类型不构建 DOM，直接调用底层组件保证性能
> 2. ensure_* 作为内置 action — 封装复杂重试逻辑
> 3. 一次性切换 — 不保留中间状态
>
> ## 修改文件清单
> 1. `brain/script_runner.py` — 核心增强 (~300行新增)：变量系统、repeat/optional、新 action handlers
> 2. `games/westgame2/scripts/*.yaml` — 新建 7 个 YAML 文件
> 3. `main.py` — 更新所有集成点 (~150行修改)
> 4. `game_profile.py` — 移除 quest_scripts 加载
> 5. 删除 `brain/quest_script.py`, `test_quest_script.py`
> 6. 新建 `test_script_runner.py` — 52 个测试
> 7. 文档更新 — `CLAUDE.md`, `quest_scripting.md`

**Files:** `brain/script_runner.py`, `main.py`, `game_profile.py`, `games/westgame2/game.json`, `games/westgame2/scripts/claim_expedition_reward.yaml`, `games/westgame2/scripts/claim_quest_reward.yaml`, `games/westgame2/scripts/collect_resource.yaml`, `games/westgame2/scripts/dispatch_citizens.yaml`, `games/westgame2/scripts/pass_expedition.yaml`, `games/westgame2/scripts/train.yaml`, `games/westgame2/scripts/upgrade_building.yaml`, `test_script_runner.py`, `CLAUDE.md`, `quest_scripting.md`

### 2. Improve step log detail

以下这个日志详细一点，把tap了什么打印出来（其他动作也是） `17:15:44 [INFO] brain.script_runner: Step 4/14: tap`

**Files:** `brain/script_runner.py`

### 3. Show actual tap coordinates in logs

像以下这种日志，没有打印出实际点击的坐标，把实际点击的坐标也打印到log `17:20:22 [INFO] brain.script_runner: Step 13/14: tap: pos=?, target={'type': 'text', 'value': '均衡配置', 'nth': -1}`

**Files:** `brain/script_runner.py`

### 4. Regenerate claim_expedition_reward.yaml from MD

根据 claim_expedition_reward.md 重新生成一下yaml

**Files:** `games/westgame2/scripts/claim_expedition_reward.yaml`
