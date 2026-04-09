# Prompt Record

- Date: 2026-04-09 00:30
- Branch: master
- Commit: fix: 采集队列检测改用 svr_lvl_user_objs 的 marchType=27/queueId=6003

---

### 1. 报告采集队列检测 bug

这个脚本好像没有正确检测现有type=21的队列状态，无论如何都会派出采集队列。
[轮次 78] 查询 AVA 地图...
[*] 玩家位置: (129, 152)
[*] 发现 378 个 coal cart
[→] 采集最近 cart: id=10300_1775557705885569 (131,157) 距离=5.4格
    剩余 377 个待采集:
      1. 10300_1775557705885882 (127,147) 距离=5.4
      2. 10300_1775557705881097 (133,156) 距离=5.7
      3. 10300_1775557705883105 (133,148) 距离=5.7
      4. 10300_1775557705876767 (134,155) 距离=5.8
      5. 10300_1775557705881332 (132,157) 距离=5.8
      ... 还有 372 个
[业务失败] cmd_name=lvl_collect_cart cmd=lvl_dispatch_pick uid=20010643 code=30001
Header: {"did": "self-system", "sid": 1, "aid": 20000118, "ksid": 1, "lvl_id": 29999, "castle_lv": 25, "battle_type": 0, "battle_id": 0, "chat_scene": ",kingdom_1", "invoker_name": "ying_test_debug", "uid": 20010643}
Param: {"march_type": 21, "unique_id": "", "target_info": {"type": 10300, "id": "10300_1775557705885569"}, "queue_id": 6003}
Response: {"res_header": {"ret_code": 30001, "cost_time_us": 0, "ret_time_s": 1775698484, "err_msg": ""}, "request": {"header": {"did": "self-system", "sid": 1, "aid": 20000118, "ksid": 1, "lvl_id": 29999, "castle_lv": 25, "battle_type": 0, "battle_id": 0, "chat_scene": ",kingdom_1", "invoker_name": "ying_test_debug", "uid": 20010643}, "request": {"cmd": "lvl_dispatch_pick", "param": {"march_type": 21, "unique_id": "", "target_info": {"type": 10300, "id": "10300_1775557705885569"}, "queue_id": 6003}}, "ex
[!] 采集派遣失败 ret_code=30001

> **Insight**
> - 之前的 bug：用 `svr_lvl_brief_objs` 里的 type=101 行军对象判断采集状态，但 brief 对象是全图共享的，字段结构也不同（扁平 vs 嵌套），导致检测不到自己的采集队列
> - 修复：改用 `svr_lvl_user_objs`，这是当前玩家的私有部队详情，包含 `objBasic.queueId` 和 `objBasic.marchType`，通过 `queueId==6003` 或 `marchType==21` 精确判断采集队列占用
> - 错误码 30001 = "Invalid operation"，就是因为采集队列已满还在重复派遣

**Files:** `scripts/collect_all_carts.py`

### 2. 指定使用 marchType=27 检测

应该使用这个marchtype=27的检测
$ python src/main.py sync 20010643 --ava 29999
[AVA] 使用指定 lvl_id=29999
同步完成 uid=20010643
  名称: p10-test-20010643
  坐标: (129,152)
  联盟: TestSquad2026 (id=20000118)
  兵种: 4 种, 总兵力 954234
  英雄: 12 个
  小队: 1
  集结: 0 个

  部队 (2 个):
    10101_20010643 type=10101 pos=12900015200 status=0 marchType=0 queueId=?
    132_1775557705886373 type=132 pos=13036014822 status=1 marchType=27 queueId=6003

> **Insight**
> - 实际采集部队的 type 是 132（不是 101），marchType 是 27（不是 21）
> - 之前的假设 marchType=21 来自 cmd_config.yaml 的请求参数，但服务器返回的部队状态用的是不同的编码
> - 可靠的判断方式：`queueId=6003`（采集专用队列）或 `marchType=27`（服务器端采集行军类型）

**Files:** `scripts/collect_all_carts.py`

### 3. 询问日志来源

"132_1775557705886373 type=132 pos=13036014822 status=1 marchType=27 queueId=6003" 这段日志是从哪里解析出来的？

### 4. L0 同步修复

这次对了。L0 命令采集矿车的时候，也用同样的方法检测已有队列。

> **Insight**
> - L0 之前的检测方式是从内存中的 `PlayerState.troops` 查 `march_type==21`，但这个数据来自 sync 阶段，可能不是最新的
> - 现在改为直接从 `lvl_battle_login_get` 响应的 `svr_lvl_user_objs` 实时检测，和脚本用同一套逻辑
> - 同时去掉了对 `self._accounts` 的依赖，减少了一个潜在的数据不一致来源

**Files:** `src/executor/l0_executor.py`
