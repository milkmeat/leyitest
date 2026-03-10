"""WestGame AI 全自动化团战系统 — 入口

用法:
  python src/main.py [--mock] <command> <args...>

查询命令:
  get_player_pos <uid>                          查询玩家坐标
  get_player_info <uid>                         查询玩家完整信息
  get_all_player_data <uid>                     查询玩家全量数据
  get_map_overview <uid>                        查询地图缩略信息
  get_map_detail <uid> [bid...]                 查询地图详细信息
  get_battle_report <uid> <report_id>           查询战报

行动命令:
  move_city <uid> <x> <y>                       移城到指定坐标
  attack_player <uid> <target_uid> <x> <y>      攻击玩家
  attack_building <uid> <building_id> <x> <y>   攻击建筑
  reinforce_building <uid> <building_id> <x> <y> 驻防建筑
  scout_player <uid> <target_uid> <x> <y>       侦察玩家
  create_rally <uid> <target_id> [prepare_time] 发起集结
  join_rally <uid> <rally_id>                   加入集结
  recall_troop <uid> <troop_id...>              召回行军部队
  recall_reinforce <uid> <unique_id>            召回增援/集结

GM 命令:
  add_gem <uid> [amount]                        添加宝石
  add_soldiers <uid> [soldier_id] [num]         添加士兵
  add_resource <uid> [op_type]                  添加资源
"""

import asyncio
import json as _json
import os
import sys

# 确保项目根目录在 sys.path 中，支持 python src/main.py 和 python -m src.main 两种方式
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def _print_json(data):
    """格式化打印 JSON"""
    print(_json.dumps(data, indent=2, ensure_ascii=False))


def _print_ret_code(resp):
    """打印响应中的 ret_code，若非 0 则输出警告"""
    code = resp.get("res_header", {}).get("ret_code", -1)
    msg = resp.get("res_header", {}).get("err_msg", "")
    if code != 0:
        print(f"[warn] ret_code={code} {msg}", file=sys.stderr)
    return code


# ---------------------------------------------------------------------------
# 查询命令
# ---------------------------------------------------------------------------


async def cmd_get_player_pos(uid_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        pos = await client.get_player_pos(uid)
        if pos:
            print(f"({pos[0]},{pos[1]})")
        else:
            print(f"无法获取 uid={uid} 的坐标", file=sys.stderr)
            sys.exit(1)
    finally:
        await client.close()


async def cmd_get_player_info(uid_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        info = await client.get_player_info(uid)
        _print_json(info)
    finally:
        await client.close()


async def cmd_get_all_player_data(uid_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        resp = await client.get_all_player_data(uid)
        _print_ret_code(resp)
        # 解析 push_list 中的每个 data item
        try:
            items = resp["res_data"][0]["push_list"][0]["data"]
            summary = {}
            for item in items:
                name = item.get("name", "")
                raw = item.get("data", "")
                try:
                    parsed = _json.loads(raw)
                    summary[name] = parsed
                except (_json.JSONDecodeError, TypeError):
                    summary[name] = raw
            _print_json(summary)
        except (KeyError, IndexError, TypeError):
            _print_json(resp)
    finally:
        await client.close()


async def cmd_get_map_overview(uid_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        resp = await client.get_map_overview(uid)
        _print_ret_code(resp)
        _print_json(resp)
    finally:
        await client.close()


async def cmd_get_map_detail(uid_str: str, *bid_args: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        bid_list = [int(b) for b in bid_args] if bid_args else []
        resp = await client.get_map_detail(uid, bid_list=bid_list)
        _print_ret_code(resp)
        _print_json(resp)
    finally:
        await client.close()


async def cmd_get_battle_report(uid_str: str, report_id: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        resp = await client.get_battle_report(uid, report_id)
        _print_ret_code(resp)
        _print_json(resp)
    finally:
        await client.close()


# ---------------------------------------------------------------------------
# 行动命令
# ---------------------------------------------------------------------------


async def cmd_move_city(uid_str: str, x_str: str, y_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid, x, y = int(uid_str), int(x_str), int(y_str)
        resp = await client.move_city(uid, x, y)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"移城成功 → ({x},{y})")
        else:
            print(f"移城失败", file=sys.stderr)
    finally:
        await client.close()


async def cmd_attack_player(uid_str: str, target_uid_str: str, x_str: str, y_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        target_uid = int(target_uid_str)
        x, y = int(x_str), int(y_str)
        resp = await client.attack_player(uid, target_uid, x, y)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"部队已出发攻击 uid={target_uid} @ ({x},{y})")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_attack_building(uid_str: str, building_id: str, x_str: str, y_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    from src.utils.coords import encode_pos
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        x, y = int(x_str), int(y_str)
        target_info = {"id": building_id, "pos": str(encode_pos(x, y))}
        march_info = {}  # 使用默认部队
        resp = await client.attack_building(uid, target_info, march_info)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"部队已出发攻击建筑 {building_id} @ ({x},{y})")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_reinforce_building(uid_str: str, building_id: str, x_str: str, y_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    from src.utils.coords import encode_pos
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        x, y = int(x_str), int(y_str)
        target_info = {"id": building_id, "pos": str(encode_pos(x, y))}
        march_info = {}
        resp = await client.reinforce_building(uid, target_info, march_info)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"部队已出发驻防建筑 {building_id} @ ({x},{y})")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_scout_player(uid_str: str, target_uid_str: str, x_str: str, y_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        target_uid = int(target_uid_str)
        x, y = int(x_str), int(y_str)
        resp = await client.scout_player(uid, target_uid, x, y)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"侦察 uid={target_uid} @ ({x},{y})")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_create_rally(uid_str: str, target_id: str, *extra: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        prepare_time = int(extra[0]) if extra else 300
        target_info = {"id": target_id}
        march_info = {}
        resp = await client.create_rally(uid, target_info, march_info, prepare_time)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"集结已发起 target={target_id} 准备时间={prepare_time}s")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_join_rally(uid_str: str, rally_id: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        target_info = {"id": rally_id}
        march_info = {}
        resp = await client.join_rally(uid, target_info, march_info)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"已加入集结 {rally_id}")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_recall_troop(uid_str: str, *troop_ids: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        if not troop_ids:
            print("请提供至少一个 troop_id", file=sys.stderr)
            sys.exit(1)
        resp = await client.recall_troop(uid, list(troop_ids))
        code = _print_ret_code(resp)
        if code == 0:
            print(f"已召回部队 {list(troop_ids)}")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_recall_reinforce(uid_str: str, unique_id: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        resp = await client.recall_reinforce(uid, unique_id)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"已召回增援 {unique_id}")
        _print_json(resp)
    finally:
        await client.close()


# ---------------------------------------------------------------------------
# GM 命令
# ---------------------------------------------------------------------------


async def cmd_add_gem(uid_str: str, *extra: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        gem_num = int(extra[0]) if extra else None
        resp = await client.add_gem(uid, gem_num)
        code = _print_ret_code(resp)
        # 解析返回的宝石数量
        try:
            items = resp["res_data"][0]["push_list"][0]["data"]
            for item in items:
                if item.get("name") == "svr_gem_stat":
                    gem_data = _json.loads(item["data"])
                    print(f"当前宝石: {gem_data.get('gem', 'N/A')}")
                    break
        except (KeyError, IndexError, TypeError):
            if code == 0:
                print("宝石设置成功")
    finally:
        await client.close()


async def cmd_add_soldiers(uid_str: str, *extra: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        soldier_id = int(extra[0]) if len(extra) > 0 else None
        soldier_num = int(extra[1]) if len(extra) > 1 else None
        resp = await client.add_soldiers(uid, soldier_id, soldier_num)
        code = _print_ret_code(resp)
        # 解析返回的士兵数据
        try:
            items = resp["res_data"][0]["push_list"][0]["data"]
            for item in items:
                if item.get("name") == "svr_soldier":
                    soldier_data = _json.loads(item["data"])
                    soldiers = soldier_data.get("list", [])
                    print("当前士兵:")
                    for s in soldiers:
                        if s.get("value", 0) > 0:
                            print(f"  id={s['id']} 数量={s['value']}")
                    break
        except (KeyError, IndexError, TypeError):
            if code == 0:
                print("士兵添加成功")
    finally:
        await client.close()


async def cmd_add_resource(uid_str: str, *extra: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        op_type = int(extra[0]) if extra else None
        resp = await client.add_resource(uid, op_type)
        code = _print_ret_code(resp)
        if code == 0:
            print("资源添加成功")
        _print_json(resp)
    finally:
        await client.close()


# ---------------------------------------------------------------------------
# 命令注册
# ---------------------------------------------------------------------------

COMMANDS = {
    # 查询
    "get_player_pos":       (cmd_get_player_pos,       "<uid>",                              "查询玩家坐标"),
    "get_player_info":      (cmd_get_player_info,      "<uid>",                              "查询玩家完整信息"),
    "get_all_player_data":  (cmd_get_all_player_data,  "<uid>",                              "查询玩家全量数据"),
    "get_map_overview":     (cmd_get_map_overview,      "<uid>",                              "查询地图缩略信息"),
    "get_map_detail":       (cmd_get_map_detail,        "<uid> [bid...]",                     "查询地图详细信息"),
    "get_battle_report":    (cmd_get_battle_report,     "<uid> <report_id>",                  "查询战报"),
    # 行动
    "move_city":            (cmd_move_city,             "<uid> <x> <y>",                      "移城到指定坐标"),
    "attack_player":        (cmd_attack_player,         "<uid> <target_uid> <x> <y>",         "攻击玩家"),
    "attack_building":      (cmd_attack_building,       "<uid> <building_id> <x> <y>",        "攻击建筑"),
    "reinforce_building":   (cmd_reinforce_building,    "<uid> <building_id> <x> <y>",        "驻防建筑"),
    "scout_player":         (cmd_scout_player,          "<uid> <target_uid> <x> <y>",         "侦察玩家"),
    "create_rally":         (cmd_create_rally,          "<uid> <target_id> [prepare_time]",   "发起集结"),
    "join_rally":           (cmd_join_rally,            "<uid> <rally_id>",                   "加入集结"),
    "recall_troop":         (cmd_recall_troop,          "<uid> <troop_id...>",                "召回行军部队"),
    "recall_reinforce":     (cmd_recall_reinforce,      "<uid> <unique_id>",                  "召回增援/集结"),
    # GM
    "add_gem":              (cmd_add_gem,               "<uid> [amount]",                     "GM: 添加宝石"),
    "add_soldiers":         (cmd_add_soldiers,          "<uid> [soldier_id] [num]",           "GM: 添加士兵"),
    "add_resource":         (cmd_add_resource,          "<uid> [op_type]",                    "GM: 添加资源"),
}


def main():
    args = sys.argv[1:]

    # 解析 --mock 参数
    env = None
    if "--mock" in args:
        env = "mock"
        args.remove("--mock")

    if len(args) < 1 or args[0] not in COMMANDS:
        print("用法: python src/main.py [--mock] <command> <args...>\n")
        print("查询命令:")
        for name in ["get_player_pos", "get_player_info", "get_all_player_data",
                      "get_map_overview", "get_map_detail", "get_battle_report"]:
            _, a, desc = COMMANDS[name]
            print(f"  {name:25s} {a:40s} {desc}")
        print("\n行动命令:")
        for name in ["move_city", "attack_player", "attack_building", "reinforce_building",
                      "scout_player", "create_rally", "join_rally", "recall_troop", "recall_reinforce"]:
            _, a, desc = COMMANDS[name]
            print(f"  {name:25s} {a:40s} {desc}")
        print("\nGM 命令:")
        for name in ["add_gem", "add_soldiers", "add_resource"]:
            _, a, desc = COMMANDS[name]
            print(f"  {name:25s} {a:40s} {desc}")
        sys.exit(1)

    cmd_name = args[0]
    func, _, _ = COMMANDS[cmd_name]
    asyncio.run(func(*args[1:], env=env))


if __name__ == "__main__":
    main()
