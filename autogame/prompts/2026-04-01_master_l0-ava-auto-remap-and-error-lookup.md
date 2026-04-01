# Prompt Record

- Date: 2026-04-01 18:40
- Branch: master
- Commit: feat: L0 AVA 命令字自动映射 + 错误码翻译

---

### 1. Run full L2-L1-L0 AVA pipeline test

跑一次(once) L2-L1-L0全链路ava测试

> **Insight**
> 全链路 Sync → L2 → L1 → L0 → 服务器 通信已打通，后续需要调优的是 L1 的决策质量和服务器业务约束处理

### 2. Add AVA command auto-remap in L0

如果有--ava 29999参数，l0就应该使用lvl命令字

> **Insight**
> 在 _dispatch 入口处通过 _AVA_ACTION_MAP 字典自动映射，L1 无需感知 AVA/普通地图差异，L0 根据 client.default_header 中的 lvl_id 自动选择正确的命令字

**Files:** `src/executor/l0_executor.py`, `src/controller/loop.py`

### 3. 21105 error meaning + add error lookup rule

21105: Please move your Haven to an open space. 记录到claude.md: 以后有遇到error code的时候，查找error_msg.yaml以获取对应的message

**Files:** `CLAUDE.md`

### 4. Add ret_code auto-translation in L0 error logging

> **Q:** L0的error code是打印在哪里的

ok（加上 ret_code 自动翻译）

**Files:** `src/executor/l0_executor.py`
