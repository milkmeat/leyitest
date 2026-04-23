# Prompt Record

- Date: 2026-04-23 19:30
- Branch: master
- Commit: fix: 移除 LVL_RECALL_TROOP 指令 + REINFORCE 队列回退 6001→6003（30001 错误减少）

---

### 1

@todo\fix_fight_cmd.md

> **Insight**
> - **队列回退设计**: 现有架构已有 `_find_fallback_queue` 回退机制（JOIN_RALLY 6004→6003→6002），本次只需扩展同一模式到 REINFORCE 场景，改动最小化
> - **采集互斥安全**: `_auto_collect_coal_carts` 每次都会查询服务器状态检查 6003 是否被占用，所以 REINFORCE 回退到 6003 后采集会自然跳过，无需额外协调逻辑

**Files:** `src/ai/prompts/l1_system_ava.txt`, `src/executor/l0_executor.py`, `todo/fix_fight_cmd.md`

### 2

commit

> **Insight**
> - **最小化改动原则**: 本次修改只删除了 L1 不应使用的指令路径，保留了枚举值和 API 方法。这样旧日志反序列化不会报错，且未来如需恢复召回功能只需重新在 prompt 中启用
> - **回退链设计**: `_find_fallback_queue` 采用优先级链模式——JOIN_RALLY 有两级回退(6003→6002)，REINFORCE 只有一级(6003)。攻击类 solo 无回退是有意为之：攻击失败比用错队列更安全
