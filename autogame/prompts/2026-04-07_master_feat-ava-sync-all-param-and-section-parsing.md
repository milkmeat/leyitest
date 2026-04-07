# Prompt Record

- Date: 2026-04-07 16:30
- Branch: master
- Commit: feat: AVA sync 增加 sync_all 参数，解析 rally/user_objs 数据段

---

### 1. 增加 sync_all 参数需求

在ava地图sync uid 玩家状态的时候，增加一个参数all=true/false, 

all=false 时只需要需要提取以下内容：    
(传入参数 all=0, 并附带以下list)                                                          
svr_lvl_brief_objs : 仅提取并保留距离玩家10格子以内的资源信息。
svr_lvl_rally_brief_objs: 当前的集结信息，如果有当前玩家发起或参与的
svr_lvl_user_objs：当前玩家在城外的所有部队信息

all=true 时，传入参数 all=0
暂时也只提取 svr_lvl_brief_objs, svr_lvl_rally_brief_objs, svr_lvl_user_objs 三种信息，
不同之处是 svr_lvl_brief_objs 保留所有对象

> **Plan**
> - `sync_all=False`（CLI 默认）: 服务器参数 `all=0` + `list=[3个section名]`，`svr_lvl_brief_objs` 距离过滤 ≤10 格
> - `sync_all=True`（CLI `--sync-all`）: 服务器参数 `all=1`，不传 list，保留全部 brief_objs
> - 两种模式都解析 3 个 section，rally 过滤 ownerUid/leaderUid 属于我方
> - 修改文件：rally.py（新增 RallyBrief）、game_api.py、data_sync.py、loop.py、main.py

> **Insight**
> 1. `all` 参数是服务器端控制：`all=1` 让服务器返回全量数据，`all=0` + `list` 让服务器只返回指定 section，减少传输量
> 2. 距离过滤是纯客户端逻辑：即使 `all=0` 服务器仍返回 section 内全部对象，10 格过滤在 `_sync_map_ava` 中用欧氏距离实现
> 3. rally 过滤用 `ownerUid`/`leaderUid` 匹配我方 UID 集合，因为 brief 级别的集结对象没有完整的 `joinerInfos`

**Files:** `src/models/rally.py`, `src/executor/game_api.py`, `src/perception/data_sync.py`, `src/controller/loop.py`, `src/main.py`

### 2. 修正 all=true 时服务器参数

> **Q:** plan 中 "all=0（不传 list）" 这里不对

"all=0（不传 list）" 这里不对，应该是 "all=1（不传 list）"，另外，给cli增加 --sync-all 参数 （默认不传，相当于all=false）

**Files:** `src/main.py`

### 3. 单账号同步打印集结和部队信息

同步单账号的时候，要打印出该账号的集结及部队信息

**Files:** `src/main.py`

### 4. 部队打印增加 queueId

每只部队对应的queueId也打印出来

**Files:** `src/main.py`
