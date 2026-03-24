# Prompt Record

- Date: 2026-03-24 12:00
- Branch: master
- Commit: feat: AVA 建筑归属识别 (lvl_aid) + LVL_REINFORCE_BUILDING 驻防命令

---

### 1. 添加 lvl_aid 并标记建筑归属

我已手动编辑accounts.yaml文件：其中alliances要记录lvl_aid信息，在ava(lvl)战场中，aid会简化成1和2
对应的, L1 llm在决策的时候，提供给llm的战场信息中，如果aid==1(我方)，应该标记为我方占有。如果aid=2标记为敌方占有

> **Insight**
> - AVA 战场的 `camp` 字段（已在 `Building.from_brief_obj` 中映射为 `alliance_id`）返回的是简化 ID（1=甲方, 2=乙方），而不是主世界的真实联盟 ID
> - 因此 `_build_nearby_buildings` 中判断 owner 时，需要用 `lvl_aid`（1 或 2）而不是主世界的 `aid`（20000118）来匹配
> - `owner_side()` 和 `get_building_control_status()` 都需要传入正确的 alliance ID

**Files:** `config/accounts.yaml`, `src/config/schemas.py`, `src/perception/l1_view.py`, `src/perception/l2_view.py`, `src/controller/loop.py`

### 2. 新增 LVL_REINFORCE_BUILDING 驻防命令

对我方已控制建筑进行增援（驻防）时，不能简单使用lvl_attack_building命令。要使用lvl_reinforce_building命令。底层都是相同的命令字协议，但是march_type不同(驻防=11)。参数日志如下：
03-24 10:06:34.347 W/Unity   (16478): {"param":{"march_type":11,"march_info":{"hero":{"vice":[7,415,8]},"leader":0,"queue_id":6001,"heros":{"3":8,"2":415,"1":7},"soldier_total_num":3,"over_defend":false,"effect_skill":{"7":{"1":712}},"carry_lord":1,"soldier":{"204":3}},"target_type":10006,"target_info":{"pos":"nil","id":"10006_1773137411102403"}}}

> **Insight**
> - march_type 的语义区分：`15`=攻打（争夺控制权），`11`=驻防增援（加入已有驻军）
> - `leader=0` 的战术意义：驻防部队以援军身份出发，不需要主帅英雄，账号可以同时驻防+solo攻击
> - `pos="nil"` 的原因：服务器通过 `target_info.id` 即可定位建筑，不需要重复传坐标

**Files:** `src/executor/l0_executor.py`, `src/executor/game_api.py`, `src/ai/prompts/l1_system_ava.txt`, `src/ai/prompts/l1_system_ava_test.txt`, `src/main.py`

### 3. 修复 target_type 和 leader 参数错误

target type应为10006而非154

$ python src/main.py lvl_reinforce_building 20010644 29999 10006_1773137411102403 154 170
...Param: {"march_type": 11, "target_info": {"id": "10006_1773137411102403", "pos": "nil", "key": 170}, "target_type": 154}

> **Insight**
> - `target_type` 误传坐标：用户传了坐标 `154 170`，被 `*extra` 吞掉解析为 `target_type=154, key=170`
> - `leader=1` 遗漏：`send_cmd` 的 `build_param` 用浅层覆盖，��传 `march_info` 时 `default_param` 中的 `leader: 1` 原样保留

**Files:** `src/executor/game_api.py`, `src/main.py`

### 4. 简化 CLI 参数

可以把这两个命令的target type / key参数都去掉了

  lvl_attack_building <uid> <lvl_id> <building_id> <x> <y> [target_type] [key]  AVA攻打建筑
  lvl_reinforce_building <uid> <lvl_id> <building_id> [target_type] [key]  AVA驻防/增援我方建筑

**Files:** `src/main.py`
