# Prompt Record

- Date: 2026-04-08 15:38
- Branch: master
- Commit: feat: 新增 uid_ava_join_all / uid_ava_leave_all 批量加入/退出 AVA 战场

---

### 1. 批量加入 AVA 战场

使用cli把accounts.yaml里面要用到的20个账号，加入test环境ava=29999 战场

> **Insight**
> 新增的 `uid_ava_join_all` 命令做了两件事：
> 1. 从 `accounts.yaml` 的 `alliances` 配置自动读取 `lvl_aid` 作为 camp_id（我方=1，敌方=2），省去手动指定
> 2. 对 `code=30001`（"has enter lvl battle"）做了幂等处理 — 已在战场的账号标记为 SKIP 而非 FAIL，这样命令可以安全重复执行

**Files:** `src/main.py`

### 2. 补充批量退出命令

那你还缺一个命令把所有uid退出ava战场

> **Insight**
> 新增了一对称命令：
> - `uid_ava_join_all <lvl_id>` — 批量 add + enter，幂等（已在战场的自动 SKIP）
> - `uid_ava_leave_all <lvl_id>` — 批量 leave，先检测 lvl_id 再退出（不在战场的自动 SKIP）
>
> 两个命令都从 `accounts.yaml` 自动读取 20 个 uid 和 camp 分配，无需手动传参。

**Files:** `src/main.py`
