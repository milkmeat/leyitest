# Prompt Record

- Date: 2026-04-09 00:00
- Branch: master
- Commit: feat: 新增全账号并发采集 AVA coal cart 脚本

---

### 1. 全账号并发采集 coal cart

写一个脚本，让ava战场上所有的账号，都去采集  coal cart

> **Insight**
> - 每个账号有独立的采集队列 `queue_id=6003`，同一时间只能采集一个 cart
> - 10 个账号并发 = 同时采集 10 个 cart，效率提升 10 倍
> - 关键难点：需要做 cart 分配去重，避免多个账号抢同一个 cart
>
> - 用 `claimed_carts` 集合 + `asyncio.Lock` 做 cart 分配去重，保证每个 cart 只被一个账号认领
> - 如果派遣失败（比如 cart 已被别人采走），会自动释放认领并尝试下一个
> - 所有 worker 共享同一个 `GameAPIClient`，底层 aiohttp session 天然支持并发连接复用

**Files:** `scripts/collect_all_accounts.py`
