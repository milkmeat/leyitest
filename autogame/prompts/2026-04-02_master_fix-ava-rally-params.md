# Prompt Record

- Date: 2026-04-02 09:50
- Branch: master
- Commit: fix: AVA 集结参数修正 (target_id/timestamp/tn_limit) + 移城重试条件放宽

---

### 1. Fix AVA move city retry condition

看一下L0在做ava移城的时候，在移城失败时，为什么没有重试周围的随机位置

> **Insight**
> 重试逻辑只覆盖了"攻击远建筑 → 自动移城 → 失败重试"这一条路径，L1 直接生成的 MOVE_CITY 通过 AVA 映射变为 LVL_MOVE_CITY 不经过 preprocess，所以 original_attack_instr 为 None

**Files:** `src/executor/l0_executor.py`

### 2. Fix AVA rally params from client log

向玩家发起的集结请求日志如下，请进行修改。（携带英雄的部分可以先不处理，只带兵）

客户端日志显示：
- target_info.id 应为 `10101_{uid}` 而非 `2_{uid}_1`
- timestamp 需要微秒级时间戳
- tn_limit 应为 1

**Files:** `src/executor/l0_executor.py`, `src/executor/game_api.py`

### 3. Test both AVA rally types

ava指令，对建筑集结，和对玩家集结，都测试一下

两个集结均返回 ret_code=0 验证通过。
