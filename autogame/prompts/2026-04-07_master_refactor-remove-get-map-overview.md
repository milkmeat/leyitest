# Prompt Record

- Date: 2026-04-07 18:30
- Branch: master
- Commit: refactor: 移除 get_map_overview，普通地图 sync 改用 game_server_login_get；修正 sid 含义；合并 dump_responses 到 collect_samples

---

### 1. sync 阶段是否使用了 get_map_brief_obj

sync状态的时候，使用 get_map_brief_obj 这个命令了吗

> **Insight**
> - 项目采用了"内部别名 → 实际命令字"的映射模式：代码层用语义化名称 `get_map_overview`，`cmd_config.yaml` 负责翻译成服务器真实命令 `get_map_brief_obj`。
> - sync 阶段的地图查询分两条路径：普通地图走 `get_map_overview`（即 `get_map_brief_obj`），AVA 战场走 `lvl_battle_login_get`，两者返回结构不同但都在 `_do_sync` 中统一处理。

### 2. 移除 get_map_overview，改用 login_get 系列

1. get_map_overview 及其相关的函数去掉，不要使用。
2. sync阶段不要调用get_map_overview ，要使用 game_server_login_get(地图) 或 lvl_battle_login_get(ava地图)，此二者返回结构相似但使用的地图场景不同
3. 可以在test server上获取game_server_login_get所返回的信息进行调试。将其原始的 json 返包保存到 docs/samples/

> **Plan**
> Step 1: 采集 game_server_login_get 样本（不同 sid），保存到 docs/samples/
> Step 2: 删除 get_map_overview 相关代码（cmd_config.yaml, game_api.py, main.py, mock_server/app.py, scripts/）
> Step 3: 重写 data_sync.py 普通地图同步，用 game_server_login_get 替换 _sync_map_both_sides + _parse_map_response
> Step 4: 更新注释和文档引用

> **Insight**
> - `game_server_login_get` (sid=1) 的 `svr_user_objs` 只包含当前玩家自己的城市（type=2，1个对象），不像 `get_map_brief_obj` 那样返回全图所有玩家和建筑。
> - AVA 战场仍然使用 `lvl_battle_login_get` 获取全图数据（建筑 + 敌方），这部分逻辑不变。

**Files:** `src/config/cmd_config.yaml`, `src/executor/game_api.py`, `src/main.py`, `mock_server/app.py`, `scripts/collect_samples.py`, `scripts/verify_cmds.py`, `src/perception/data_sync.py`, `src/models/building.py`, `docs/samples/game_server_login_get__sid0__20001946.json`, `docs/samples/game_server_login_get__sid1__20001946.json`

### 3. 普通地图只需要自己的数据

> **Q:** 采样结果显示 game_server_login_get (sid=1) 的 svr_user_objs 只包含当前玩家自己的城市。你的意图是？

只需要自己的数据

### 4. 修正 sid 含义

sid=0, sid=1 不是主城/地图的意思。这个游戏是分服务器的。sid=0表示0号服务器，sid=1表示1号服务器。每个玩家创号的时候会分配所属的服务器。在test server中，只有sid=1 。记录到test-enf-info skill，并更改相关的注释、参数

> **Insight**
> - `sid` 是 server ID 的缩写，游戏是分服架构，每个玩家创号时分配到某个服务器。test 环境只开了 sid=1，所以之前 sid=0 的请求返回 30100（服务器不可达）不是因为"主城场景不存在"，而是 0 号服务器根本没开。

**Files:** `.claude/skills/test-env-info/SKILL.md`, `config/env_config.yaml`, `scripts/collect_samples.py`, `src/executor/game_api.py`

### 5. 合并 dump_responses 到 collect_samples

删除 dump_responses.py, 合并进 collect_samples.py

**Files:** `scripts/dump_responses.py`, `scripts/collect_samples.py`
