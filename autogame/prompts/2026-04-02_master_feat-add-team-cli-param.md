# Prompt Record

- Date: 2026-04-02 18:30
- Branch: master
- Commit: feat: 添加 --team <1|2> 全局参数，支持切换管理我方/敌方

---

### 1. 实现 switch_team.md 任务

你来完成 switch_team.md

> **Plan**
> 采用"配置交换"方案，当 --team 2 时在 load_all() 返回后交换 accounts/enemies 和 alliances.ours/enemy。所有下游代码（DataSyncer、AIController、L0Executor）通过 active_uids()/alliances.ours 等访问器间接获取数据，零改动。只修改 src/main.py 一个文件。

> **Insight**
> 配置系统已内置联盟切换基础设施（SquadsConfig.set_active()、load_all(alliance=...)），采用"配置交换"方案只需修改 CLI 层和配置加载层。所有下游模块通过 config.accounts.active_uids()、config.squads.squads、config.accounts.alliances.ours 等访问器获取数据而非硬编码，这使得配置层交换能全局生效——这是依赖倒置原则（DIP）的经典体现。

**Files:** `src/main.py`, `todo/switch_team.md`

### 2. 确认 AVA camp_id 映射正确性

在调用ava命令的时候，需要传入camp_id参数，正确对应到team上面了吗

> **Insight**
> camp_id 在 AVA 系统中有两种角色：注册时（ava_add_player）手动传入；战斗时（run 循环中所有操作）服务器自动识别阵营，客户端通过 alliances.ours.lvl_aid 判断建筑归属。Config swap 后 lvl_aid 自动映射到正确值。

**Files:** (无代码改动，分析确认)
