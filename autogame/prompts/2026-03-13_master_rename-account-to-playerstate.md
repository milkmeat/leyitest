# Prompt Record

- Date: 2026-03-13 00:00
- Branch: master
- Commit: rename Account model to PlayerState to disambiguate from config/accounts.yaml

---

### 1. Rename model to avoid confusion with config

src\models\account.py 和 config/accounts.yaml 都将account，令人困惑。给换个名字

> **Insight**
> - `Account` 这个名字暗示的是"登录凭证/身份"，但实际模型包含了士兵、英雄、Buff、部队行军等完整运行时状态
> - 重命名为 `PlayerState` 更准确地表达了"从服务器同步回来的玩家当前状态快照"这一语义
> - 这样 `accounts.yaml`（静态身份清单）和 `PlayerState`（动态运行时状态）概念完全分离

**Files:** `src/models/account.py`, `src/models/player_state.py`, `src/models/__init__.py`, `src/models/enemy.py`, `src/perception/data_sync.py`, `src/perception/l1_view.py`

### 2. Choose rename direction

> **Q:** 你想重命名哪一边来消除歧义？(重命名模型 / 重命名配置文件 / 两边都改)

重命名模型 (推荐) — Account → PlayerState，account.py → player_state.py。config/accounts.yaml 保持不变
