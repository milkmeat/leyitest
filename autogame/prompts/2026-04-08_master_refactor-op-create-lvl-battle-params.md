# Prompt Record

- Date: 2026-04-08 16:00
- Branch: master
- Commit: refactor: 更新 op_create_lvl_battle 参数结构（lvl_id/camp/begin_time/duration）

---

### 1. 修改 op_create_lvl_battle 调用参数

修改一下op_create_lvl_battle的调用参数，不确定的向我询问
        "op_create_lvl_battle": {
            "action": 0,
            "op": 1,
            "optional_param": {
                "num_limit": 30
            },
            "param": {
                "begin_time": 0,
                "camp": [
                    {
                        "aid": 1,
                        "al_flag": 1,
                        "al_name": "al_name_1",
                        "al_nick": "al_nick_1",
                        "main": {},
                        "vice": {}
                    },
                    {
                        "aid": 2,
                        "al_flag": 2,
                        "al_name": "al_name_2",
                        "al_nick": "al_nick_2",
                        "main": {},
                        "vice": {}
                    }
                ],
                "end_time": 0,
                "event_id": "",
                "lvl_id": 0,
                "num_limit": 0
            },
            "version": "1.0"
        },

**Files:** `src/config/cmd_config.yaml`, `src/main.py`, `mock_server/app.py`, `scripts/verify_cmds.py`, `docs/references/cmd_config.yaml`

### 2. 确认 action/op/version 等字段处理方式

> **Q:** action/op/version/optional_param 这些字段应该放在哪一层？

action, op, version, optional_param 这几个参数可以忽略，服务器不做检查

### 3. 确认 camp 中 main/vice 含义

> **Q:** camp 里的 main 和 vice 是什么含义？当前实现用的是 uid_list 列表，新协议改成了 main/vice 对象。

main/vice留空即可，样例如下：[{"aid":1,"al_nick":"al_nick_1","al_name":"al_name_1","al_flag":1,"main":{},"vice":{}},{"aid":2,"al_nick":"al_nick_2","al_name":"al_name_2","al_flag":2,"main":{},"vice":{}}]

### 4. 确认战场ID字段名

> **Q:** 原来的 1v1_id 参数现在是否对应 param.lvl_id？

1v1是错误写法，应该是lvl.我刚才手动修改了一下cmd_config.yaml

### 5. uid_list 保留为占位符

uid_list需要放在缺省参数里面作为占位符。我手动在cmd_config.yaml里面加回去了。一开始创建战场的时候随便填一些uid.以后真正的队员可以用cli工具加进名单

**Files:** `src/config/cmd_config.yaml`

### 6. 确认 begin_time/end_time 处理

begin_time使用当前秒数，end_time使用365 day之后的秒数

**Files:** `src/config/cmd_config.yaml`, `src/main.py`, `docs/references/cmd_config.yaml`

### 7. 添加 duration 可选参数

cli加一个可选参数duration，表示end_time在多少个小时以后，默认仍然是365天，例如："python src/main.py uid_ava_create <lvl_id> [duration=n_hours]"

**Files:** `src/main.py`
