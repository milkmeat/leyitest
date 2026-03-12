# Prompt Record

- Date: 2026-03-12 21:40
- Branch: master
- Commit: fix create_rally and join_rally protocol to match real game client

---

### 1. Provide client log for create_rally protocol correction

发起集结日志如下，请以此修正协议和参数
```
{"param":{"prepare_time":300,"target_info":{"id":"2_20010668_1"},"tn_limit":1,"march_type":13,"march_info":{"effect_skill":{"7":{"1":712}},"queue_id":6001,"carry_lord":1,"over_defend":false,"leader":1,"soldier_total_num":1450,"heros":{"1":7,"3":415,"2":21},"soldier":{"204":1450},"hero":{"vice":[7,21,415]}},"target_type":2,"timestamp":"1773320865935600","recommand_troop":[]}}
```

> **Insight**
> - `tn_limit: 1` — 必须有，之前遗漏
> - `timestamp` 是微秒字符串，不是整数 0
> - `hero.vice` 应为数组 `[]` 而非对象 `{}`
> - `target_info` 不需要 `pos` 字段（create_rally 场景）

**Files:** `src/config/cmd_config.yaml`, `src/main.py`, `src/executor/game_api.py`

### 2. Move A2 near B before join test

先把20010644 移城到B旁边

### 3. Create rally with 500 soldiers for testing

让A1再次发起集结，但只带500士兵

### 4. Provide client log for join_rally protocol correction

响应集结的日志如下，先修改程序，等我指令再开始测试
```
{"param":{"target_type":107,"march_info":{"queue_id":6001,"effect_skill":{"7":{"1":712}},"leader":0,"hero":{"vice":[7,413,415]},"heros":{"1":7,"2":413,"3":415},"over_defend":false,"carry_lord":1,"soldier_total_num":4500,"soldier":{"204":4500}},"target_info":{"id":"107_1773314190255521_1","pos":50700050100},"march_type":12}}
```

> **Insight**
> join_rally 与 create_rally 的协议差异很大：
> 1. `march_type=12`（加入集结）vs `13`（发起集结）— 两个不同的行军类型
> 2. `target_type=107`（rally 对象）vs `2`（城市）— 加入的目标是 rally 本身
> 3. `target_info` 需要包含 `pos`（rally 集结点编码坐标）
> 4. `leader=0`（加入者）vs `leader=1`（发起者）

**Files:** `src/config/cmd_config.yaml`, `src/main.py`, `test_rally.sh`

### 5. Test create + join rally end-to-end

可以测试集结与响应了。只派500士兵

> **Insight**
> create_rally + join_rally 在 test server 上均 ret_code=0，协议完全验证通过。
> rally ID 格式为 `{type}_{timestamp}_{key}`，其中 type=107 是 rally 对象类型。
