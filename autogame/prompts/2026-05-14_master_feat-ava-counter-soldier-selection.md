# Prompt Record

- Date: 2026-05-14 17:40
- Branch: master
- Commit: feat: AVA 攻击自动选择克制兵种

---

### 1

/plan 为ava战场的对战实现以下功能: 1. 对其余建筑/玩家发起进攻时先查询目标驻防部队信息 2. 选择最强克制对方兵种攻击 3. 派出士兵数量可配置281000

**Files:** `src/utils/counter.py`, `src/perception/defender_probe.py`, `src/executor/l0_executor.py`, `src/config/schemas.py`, `config/activity.yaml`

### 2

> **Q:** 当无法获取驻防详情时（scout 异步/无数据），兜底策略选哪个？

均匀分布兜底（三等分），无数据时默认 Shooter

**Files:** `src/perception/defender_probe.py`

### 3

/plan 先做测试，按 @todo\attack_test.md 完成

**Files:** `attack_test.sh`, `attack_find_building.py`, `todo/attack_test.md`

### 4

补充到 @todo\attack_test.md: 创建战场之后，要等待4分钟再进入。游戏机制中有3分钟准备时间，此时无法发动进攻

**Files:** `todo/attack_test.md`, `attack_test.sh`

### 5

> **Q:** B 账号(20010668)是敌方 uid，L0 校验会拒绝。如何处理？

cli的L0命令应该加上一个可选参数 camp=1 or 2 表示是在操作我方还是敌方账号，默认为1

**Files:** `src/main.py`, `src/executor/l0_executor.py`

### 6

检查代码中的克制关系使用是否正确：Basher is Strong against Piercer, Shooter is Strong against Basher, Piercer is Strong against Shooter.

> **Insight**
> 代码中的 `COUNTER_OF` 映射与游戏官方 `doc_soldier.yaml` 中声明的 "Strong against" / "Weak against" 完全一致。注意 `CLAUDE.md` 中的描述 `archer > infantry > cavalry > archer` 容易造成混淆 — 这里的 archer/infantry/cavalry 对应的是 Shooter/Basher/Piercer，但命名与传统 SLG 不同。

### 7

/plan 根据本会话的需求，对尚未提交的代码做code review (这是另一个ai写的代码)

> **Insight**
> Code Review 发现 10 个问题：P0 building.py 重复字段声明；P1 方法命名误导、_COUNTER_ACTIONS 包含不适用 action、--camp 无校验、ATTACK_PLAYER 无效；P2 方法内 import、缺少边界测试等。

**Files:** `src/models/building.py`, `src/executor/l0_executor.py`, `src/main.py`, `tests/test_counter.py`
