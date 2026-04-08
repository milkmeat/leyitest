# Prompt Record

- Date: 2026-04-08 16:30
- Branch: master
- Commit: feat: 增强 loop 日志，记录 L2/L1 输入输出及 L0 命令执行结果

---

### 1. 增强 logs/ 目录下的 JSON 日志

logs/目录下的json文件没有记录太多有用的东西，需要增加：
1. l1, l2的所有输入、输出
2. l0 所产生的所有命令字及执行结果（成功、失败）
3. 文件名需要加上 team信息、时间戳信息，避免被覆盖

> **Plan**
> 在 L2Commander / L1Leader 上缓存每轮的 input/output（last_input/last_output 属性），然后在 _write_log 中统一收集写入增强版 JSON 日志。文件名格式 {alliance_name}_loop_{id}_{YYYYMMDD_HHmmss}.json。涉及 3 个文件，约 70 行新增代码，无 API 签名变更。
>
> 修改清单：
> 1. src/ai/l2_commander.py — __init__ 新增 last_input/last_output，decide() 中赋值
> 2. src/ai/l1_leader.py — 同上，每个 L1Leader 独立实例避免并行竞态
> 3. src/controller/loop.py — _write_log 重写为增强版，新增 _build_l2_log/_build_l1_log/_build_l0_log，调用点从 run() 移入 _run_one_loop 内部

> **Insight**
> 把 last_input/last_output 存在各 Leader 实例上而非 LLMClient 上，避免了 L1 并行 asyncio.gather 时的竞态问题——每个 L1Leader 是独立对象，天然线程安全。json.dump 的 default=str 兜底处理了 Enum 等不可序列化类型。

**Files:** `src/ai/l2_commander.py`, `src/ai/l1_leader.py`, `src/controller/loop.py`
