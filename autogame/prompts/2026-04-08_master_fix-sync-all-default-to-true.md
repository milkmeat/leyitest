# Prompt Record

- Date: 2026-04-08 00:00
- Branch: master
- Commit: fix: sync_all 默认改为 True，使用 --no-sync-all 切换精简模式

---

### 1. 排查 L2 输入缺失 AVA 建筑信息

检查一下现在提供给L2的输入信息里面，为什么没有ava战场的建筑信息了。我使用"python src/main.py sync --ava 29999 --sync-all" 可以看到10个建筑。是不是l2在循环中没有带上sync all参数

> **Plan**
> 根因：`sync_all` 默认为 `False`，导致两层过滤叠加：1) 服务端过滤：`all=0` 让服务器只返回部分数据；2) 客户端距离过滤：`NEARBY_RADIUS = 10` 格，丢弃远处建筑。修改方案：将 `--sync-all` 参数改为 `--no-sync-all`（反向语义），默认 `sync_all = True`，遇到 `--no-sync-all` 时设为 `False`。涉及 `src/main.py` run/sync 命令参数解析、帮助文本、`src/controller/loop.py` 注释更新。

> **Insight**
> 问题的本质是 `NEARBY_RADIUS = 10` 这个距离过滤对 AVA 战场不合理。AVA 是封闭副本，地图上总共只有约 10 个建筑，它们分布在整个战场各处，不可能都在某个玩家 10 格范围内。而 L2 指挥官需要全局建筑态势才能做战略决策，所以 AVA 模式下应该无条件全量同步。

**Files:** `src/main.py`, `src/controller/loop.py`

### 2. 要求 sync_all 默认为 True

> **Q:** 初始计划是仅在 AVA 模式下强制 sync_all=True，用户要求更改方案。

把sync-all默认改成true, 除非用户在cli参数中指定为false

> **Insight**
> 这次改动的核心是把 `sync_all` 的默认语义从 opt-in 翻转为 opt-out。原来需要显式 `--sync-all` 才能全量同步，现在默认全量，需要 `--no-sync-all` 才走精简模式。同时保留了对旧参数 `--sync-all` 的兼容过滤，避免它被误解析为 uid。
