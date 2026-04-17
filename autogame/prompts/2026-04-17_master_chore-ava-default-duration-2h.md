# Prompt Record

- Date: 2026-04-17 00:00
- Branch: master
- Commit: chore: AVA 战场默认保留时长改为 2 小时

---

### 1. AVA 战场默认保留时长改为 2 小时

把 op_create_lvl_battle 创建ava战场的默认保留时长改成 2 hour，ava_simulate.sh 里面，也使用 2 hour 创建ava测试战场

> **Insight**
> - `cmd_uid_ava_create` 的 `duration=` 参数单位是**小时**，直接乘 3600 转为秒后加到 `begin_time` 上得到 `end_time`
> - `ava_simulate.sh` 里显式传 `duration=2` 是为了确保脚本行为不依赖默认值——即使将来默认值再改，脚本也始终创建 2 小时战场

**Files:** `src/main.py`, `ava_simulate.sh`
