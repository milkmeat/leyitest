# Prompt Record

- Date: 2026-03-11 23:36
- Branch: master
- Commit: add solo attack integration test with CLI commands and march_info fix

---

### 1. Complete the test_l0_solo_attack.md task

你来完成 test_l0_solo_attack.md

> **Insight**
> Solo Attack 测试的关键设计点：
> 1. 坐标联动 — B 先移城到随机位置，A 再移到 B 旁边 (x+1, y)。攻击/侦察命令需要传入 B 的实际坐标，所以必须先查询 B 的位置
> 2. Mock vs Test 差异 — Mock 服务器只记录 troop 派遣但不模拟战斗结算，所以 "士兵减少" 验证只能在 test 环境通过。Mock 模式下需要跳过该检查或标记为 SKIP
> 3. add_soldiers 是 ADD 行为 — 我们先读取当前兵力，再添加随机数量，读回验证 = old + added，这也是测试项之一

**Files:** `test_solo.sh`, `mock_server/mock_data.yaml`, `todo/test_l0_solo_attack.md`

### 2. Fix city offset from +1 to +3

由于主城有一定宽度，在A移城到B旁边时，+1不够。要使用+3

> **Insight**
> +3 仍然被占用 (21105) — test 服务器上有很多账号，固定偏移不可靠。需要加重试机制，尝试多个方向和距离。

**Files:** `test_solo.sh`

### 3. Specify soldier type and count for dispatch_troop

dispatch_troop需要指定兵种和数量，就使用你前面add_soldier的那个兵种。数量填5000 (游戏有出征上限。现在我们没读取这个值，先填一个较小的数确保成功。)

**Files:** `src/main.py`, `test_solo.sh`

### 4. Fix march_info hero and extra fields

默认不要带英雄，把hero信息去掉. carry_lord和 leader字段也去掉

**Files:** `src/main.py`

### 5. Provide correct march_info format

按这样组装
{
            'cmd_name': 'attack_city',
            'header': header,
            'param': {
                'target_type': 2,
                'march_info': {
                    'hero': {'vice': {}},
                    'over_defend': False,
                    'leader': 1,
                    'soldier_total_num': soldier_num,
                    'heros': {},
                    'queue_id': 6001,
                    'soldier': {str(soldier_id): soldier_num},
                    'carry_lord': 1
                },
                'march_type': 2,
                'target_info': {
                    'pos': pos,
                    'id': target_id
                }
            }
        }

> **Insight**
> dispatch_troop 的 march_info 必须包含完整字段：
> - queue_id: 6001 — 指定出征队列（主队列）
> - soldier_total_num — 出征总兵力数
> - leader: 1 — 使用主队列
> - carry_lord: 1 — 携带领主
> - hero/heros — 即使为空也需要传空对象 {}
> - over_defend: false — 不驻扎直接回城

**Files:** `src/main.py`
