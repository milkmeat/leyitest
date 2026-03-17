# Prompt Record

- Date: 2026-03-17 18:30
- Branch: master
- Commit: feat: add get_player_lvl_info to detect AVA battlefield presence

---

### 1. Add get_player_lvl_info command

以下命令字可以获取玩家是否在ava战场的信息
返回值中 lvl_id 为0 则是在普通地图。非0 即对应的ava战场副本id

  get_player_lvl_info:
    cmd: "login_get"
    default_param:
      all: 0
      list:
        - "svr_player_lvl_info"
    description: "获取玩家临时战场信息（判断是否在ava临时战场）"

> **Insight**
> 1. 这个查询是 AVA 战场指令路由的基石：主循环的 Phase 1 (Sync) 阶段可以先调用 get_player_lvl_info 判断玩家是否在 AVA 战场中，然后决定后续使用主世界指令集还是 LVL_* 指令集。
> 2. 返回值设计为 int 而非 bool：返回 lvl_id 而不是简单的布尔值，因为系统可能需要把 lvl_id 传给其他 AVA 命令（如 lvl_battle_login_get(lvl_id)），避免二次查询。

**Files:** `src/config/cmd_config.yaml`, `src/executor/game_api.py`

### 2. Test all UIDs for AVA battlefield presence

测试一下所有的uid，看看有没有已经进入ava战场的

> **Insight**
> 1. lvl_id=29999 是同一个战场副本：两个账号 acc_04(20010646) 和 enemy_02(20010669) 的 lvl_id 相同，说明它们正在同一个 AVA 战场实例中对战。
> 2. 62 个账号并发查询无一失败，说明服务器连接稳定，login_get + svr_player_lvl_info 协议可以安全地用于主循环的 Phase 1 批量同步。

### 3. Query lvl_battle_login_get for battlefield details

lvl_battle_login_get 查询一下看看

> **Insight**
> 1. 返回数据极其丰富：lvl_battle_login_get 一次请求返回了 10 个数据块，涵盖地图全貌 (svr_lvl_brief_objs)、参战名单 (svr_lvl_joiner_info)、自己的详细对象 (svr_lvl_user_objs)、战况积分 (svr_lvl_war_situation) 等。这是 AVA 战场的"全量同步"接口。
> 2. 建筑 type 编码体系：10000=堡垒、10001=哨塔、10002=资源点、10103=纪念碑、10104=兵营、10006=佣兵营、10101=玩家主城。
> 3. acc_04 兵力为负数 (-219996) 是异常信号——可能是之前测试中被击败导致兵力扣减到负数，后续 _build_march_info 需要对负数兵力做防御处理。
