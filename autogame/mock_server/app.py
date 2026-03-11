"""Mock 游戏服务器 — FastAPI 应用

兼容真实 test 服务器的 GET 协议:
  GET {base_url}?{json_body}

json_body 格式:
  {"header": {..., "uid": xxx}, "request": {"cmd": "xxx", "param": {...}}, "extra_info": {...}}

启动方式:
  cd mock_server && python app.py
  或: uvicorn mock_server.app:app --port 18888
"""

import json
import os
import sys
import time
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import unquote

# 确保项目根目录在 sys.path 中
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import yaml
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.utils.coords import encode_pos, decode_pos

# ---------------------------------------------------------------------------
# 数据加载
# ---------------------------------------------------------------------------

MOCK_DATA_PATH = Path(__file__).resolve().parent / "mock_data.yaml"


def load_mock_data() -> Dict[str, Any]:
    with open(MOCK_DATA_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# 启动时加载，运行期间可变（action 命令会修改内存状态）
MOCK_DATA = load_mock_data()

app = FastAPI(title="WestGame Mock Server")


# ---------------------------------------------------------------------------
# 响应构造辅助
# ---------------------------------------------------------------------------


def _ok_response(data_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """构造成功响应（与真实服务器格式一致）"""
    return {
        "res_header": {"ret_code": 0, "cost_time_us": 0, "ret_time_s": int(time.time()), "err_msg": ""},
        "res_data": [{"push_list": [{"data": data_items, "main": 1}], "push_result": 0}],
    }


def _error_response(code: int, msg: str) -> Dict[str, Any]:
    """构造错误响应"""
    return {
        "res_header": {"ret_code": code, "cost_time_us": 0, "ret_time_s": int(time.time()), "err_msg": msg},
        "res_data": [],
    }


def _data_item(name: str, data: Any) -> Dict[str, str]:
    """构造单个 data item"""
    return {"name": name, "data": json.dumps(data, ensure_ascii=False)}


def _get_player(uid: int) -> Dict[str, Any] | None:
    return MOCK_DATA.get("players", {}).get(uid)


# ---------------------------------------------------------------------------
# 命令处理器
# ---------------------------------------------------------------------------


def handle_login_get(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理 login_get 命令 (get_player_info)"""
    requested = param.get("list", [])
    data_items = []
    player = _get_player(uid)

    if "svr_lord_info_new" in requested and player:
        city_pos = encode_pos(player["x"], player["y"])
        lord_data = {
            "lord_info_data": {
                "cur_state": 0,
                "lord_info": {
                    "aid": player.get("alliance_id", 0),
                    "city_level": player.get("city_level", 25),
                    "avatar": 0,
                    "uid": uid,
                    "ksid": 1,
                    "head_frame": 0,
                    "skin_id": 0,
                    "city_pos": str(city_pos),
                    "uname": player.get("name", ""),
                    "al_name": player.get("alliance", ""),
                    "al_nick": "",
                    "lord_level": player.get("lord_level", 60),
                    "custom_avatar": "",
                },
            }
        }
        data_items.append(_data_item("svr_lord_info_new", lord_data))

    if "svr_player" in requested and player:
        city_pos = encode_pos(player["x"], player["y"])
        player_data = {
            "uid": uid,
            "cid": city_pos,
            "cname": player.get("name", ""),
            "level": player.get("lord_level", 60),
            "vip_level": player.get("vip_level", 1),
            "al_id": player.get("alliance_id", 0),
            "al_name": player.get("alliance", ""),
            "status": 0,
            "dead": 0,
            "force": str(player.get("power", 0)),
        }
        data_items.append(_data_item("svr_player", player_data))

    if "svr_soldier" in requested and player:
        soldiers = player.get("soldiers", [{"id": 204, "value": 100000}])
        data_items.append(_data_item("svr_soldier", {"list": soldiers}))

    if "svr_hero_list" in requested and player:
        heroes = player.get("heroes", [{"id": 21, "lv": 60, "state": 0, "skill_lv": [1, 1, 1]}])
        data_items.append(_data_item("svr_hero_list", {"heros": heroes}))

    if "svr_buff" in requested and player:
        buffs = player.get("buffs", [])
        data_items.append(_data_item("svr_buff", {"buff_item": buffs}))

    if "svr_gem_stat" in requested and player:
        data_items.append(_data_item("svr_gem_stat", {"gem": player.get("gem", 0)}))

    return _ok_response(data_items)


def handle_game_server_login_get(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理 game_server_login_get 命令 (get_all_player_data)"""
    player = _get_player(uid)
    if not player:
        return _error_response(30001, f"player {uid} not found")

    data_items = []
    city_pos = encode_pos(player["x"], player["y"])

    # svr_user_objs — 主城对象信息
    user_obj = {
        "objs": [{
            "uniqueId": f"2_{uid}_1",
            "objBasic": {
                "type": 2, "id": str(uid), "pos": str(city_pos),
                "sid": 1, "uid": str(uid), "aid": str(player.get("alliance_id", 0)),
            },
            "cityInfo": {
                "uname": player.get("name", ""),
                "level": player.get("city_level", 25),
                "force": str(player.get("power", 0)),
                "vipLevel": str(player.get("vip_level", 1)),
                "alName": player.get("alliance", ""),
            },
        }]
    }
    data_items.append(_data_item("svr_user_objs", user_obj))

    # svr_soldier
    soldiers = player.get("soldiers", [])
    data_items.append(_data_item("svr_soldier", {"list": soldiers}))

    # svr_hero_list
    heroes = player.get("heroes", [])
    data_items.append(_data_item("svr_hero_list", {"heros": heroes}))

    # svr_gem_stat
    data_items.append(_data_item("svr_gem_stat", {"gem": player.get("gem", 0)}))

    # svr_march_list — 行军队列
    troops = player.get("troops", [])
    data_items.append(_data_item("svr_march_list", {"list": troops}))

    return _ok_response(data_items)


def handle_fixed_move_city_new(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理移城命令"""
    player = _get_player(uid)
    if not player:
        return _error_response(30001, f"player {uid} not found")

    tar_pos = param.get("tar_pos", 0)
    x, y = decode_pos(int(tar_pos))
    old_x, old_y = player["x"], player["y"]
    player["x"] = x
    player["y"] = y

    # 移城同时召回所有在外部队
    recalled = len(player.get("troops", []))
    player["troops"] = []

    city_pos = encode_pos(x, y)
    obj_data = {
        "objs": [{
            "uniqueId": f"2_{uid}_1",
            "objBasic": {"type": 2, "id": str(uid), "pos": str(city_pos), "uid": str(uid)},
            "cityInfo": {"uname": player.get("name", ""), "force": str(player.get("power", 0))},
        }]
    }
    data_items = [_data_item("svr_user_objs", obj_data)]

    print(f"  [mock] move_city uid={uid}: ({old_x},{old_y}) → ({x},{y}), recalled {recalled} troops")
    return _ok_response(data_items)


def handle_dispatch_troop(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理 dispatch_troop (attack_player, attack_building, reinforce_building, join_rally)"""
    player = _get_player(uid)
    if not player:
        return _error_response(30001, f"player {uid} not found")

    march_type = param.get("march_type", 0)
    target_info = param.get("target_info", {})
    march_info = param.get("march_info", {})

    troop_id = f"108_{int(time.time()*1000)}_{len(player.get('troops', [])) + 1}"

    march_type_names = {2: "attack", 11: "reinforce", 13: "rally_join"}
    action = march_type_names.get(march_type, f"type_{march_type}")

    troop_entry = {
        "unique_id": troop_id,
        "march_type": march_type,
        "target_info": target_info,
        "march_info": march_info,
        "start_time": int(time.time()),
        "status": "marching",
    }
    player.setdefault("troops", []).append(troop_entry)

    data_items = [_data_item("svr_march_event", {
        "unique_id": troop_id,
        "march_type": march_type,
        "status": "dispatched",
    })]

    print(f"  [mock] dispatch_troop uid={uid} action={action} troop_id={troop_id} target={target_info}")
    return _ok_response(data_items)


def handle_dispatch_scout(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理侦察命令 — 即时返回目标信息"""
    tar_pos = param.get("tar_pos", 0)
    x, y = decode_pos(int(tar_pos))

    # 查找目标位置的玩家
    target_player = None
    for pid, pdata in MOCK_DATA.get("players", {}).items():
        if pdata["x"] == x and pdata["y"] == y:
            target_player = pdata
            target_player["_uid"] = pid
            break

    scout_result = {"tar_pos": tar_pos, "x": x, "y": y}
    if target_player:
        scout_result.update({
            "target_uid": target_player["_uid"],
            "name": target_player.get("name", ""),
            "power": target_player.get("power", 0),
            "soldiers": target_player.get("soldiers", []),
            "alliance": target_player.get("alliance", ""),
        })
    else:
        scout_result["target_uid"] = 0
        scout_result["name"] = "empty"

    data_items = [_data_item("svr_scout_result", scout_result)]
    print(f"  [mock] scout uid={uid} pos=({x},{y}) found={'yes' if target_player else 'no'}")
    return _ok_response(data_items)


def handle_create_rally_war(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理发起集结"""
    player = _get_player(uid)
    if not player:
        return _error_response(30001, f"player {uid} not found")

    target_info = param.get("target_info", {})
    march_info = param.get("march_info", {})
    prepare_time = param.get("prepare_time", 300)

    rally_id = f"rally_{uid}_{int(time.time())}"
    rally = {
        "rally_id": rally_id,
        "creator_uid": uid,
        "target_info": target_info,
        "march_info": march_info,
        "prepare_time": prepare_time,
        "create_time": int(time.time()),
        "members": [uid],
    }
    MOCK_DATA.setdefault("rallies", {})[rally_id] = rally

    data_items = [_data_item("svr_rally_info", {
        "rally_id": rally_id,
        "status": "preparing",
        "creator_uid": uid,
        "prepare_time": prepare_time,
    })]

    print(f"  [mock] create_rally uid={uid} rally_id={rally_id} target={target_info}")
    return _ok_response(data_items)


def handle_recall_reinforce(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理召回增援/集结"""
    unique_id = param.get("unique_id", "")
    player = _get_player(uid)
    if not player:
        return _error_response(30001, f"player {uid} not found")

    # 从 troops 中移除匹配的
    troops = player.get("troops", [])
    found = False
    player["troops"] = [t for t in troops if t.get("unique_id") != unique_id or not (found := True)]  # noqa: F841

    # 也检查 rallies
    rallies = MOCK_DATA.get("rallies", {})
    if unique_id in rallies:
        del rallies[unique_id]
        found = True

    if not found:
        return _error_response(30001, f"unique_id {unique_id} not found")

    data_items = [_data_item("svr_recall_result", {"unique_id": unique_id, "status": "recalled"})]
    print(f"  [mock] recall_reinforce uid={uid} unique_id={unique_id}")
    return _ok_response(data_items)


def handle_change_troop(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理召回行军部队 (recall_troop)"""
    march_info = param.get("march_info", {})
    ids = march_info.get("ids", [])
    player = _get_player(uid)
    if not player:
        return _error_response(30001, f"player {uid} not found")

    troops = player.get("troops", [])
    recalled = []
    remaining = []
    for t in troops:
        if t.get("unique_id") in ids:
            recalled.append(t["unique_id"])
        else:
            remaining.append(t)
    player["troops"] = remaining

    if not recalled:
        return _error_response(30001, f"no matching troops for ids={ids}")

    data_items = [_data_item("svr_troop_recall", {"recalled": recalled})]
    print(f"  [mock] recall_troop uid={uid} recalled={recalled}")
    return _ok_response(data_items)


def handle_get_map_brief_obj(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理地图缩略信息查询

    输出格式与真实服务器一致:
      data item name = "svr_map_brief_objs"
      data = {"briefList": [{uniqueId, objBasic: {type, pos, uid, aid, ...}}, ...]}
    """
    buildings = MOCK_DATA.get("buildings", {})
    players = MOCK_DATA.get("players", {})

    brief_list = []
    # 添加玩家城市 (type=2)
    for pid, pdata in players.items():
        pos = encode_pos(pdata["x"], pdata["y"])
        brief_list.append({
            "uniqueId": f"2_{pid}_1",
            "objBasic": {
                "type": 2,
                "pos": str(pos),
                "uid": str(pid),
                "aid": str(pdata.get("alliance_id", 0)),
                "sid": 1,
            },
        })
    # 添加建筑
    for bid, bdata in buildings.items():
        pos = encode_pos(bdata["x"], bdata["y"])
        brief_list.append({
            "uniqueId": bid,
            "objBasic": {
                "type": bdata.get("type", 27),
                "pos": str(pos),
                "key": bdata.get("id", 0),
                "aid": str(bdata.get("alliance_id", 0)),
                "alName": bdata.get("owner_alliance", ""),
                "sid": 1,
                "status": bdata.get("status", 0),
                "fightFlag": bdata.get("fight_flag", 0),
            },
        })

    data_items = [_data_item("svr_map_brief_objs", {"briefList": brief_list})]
    return _ok_response(data_items)


def handle_game_svr_map_get(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理地图详细信息查询"""
    bid_list = param.get("bid_list", [])
    buildings = MOCK_DATA.get("buildings", {})

    block_data = []
    for bid, bdata in buildings.items():
        pos = encode_pos(bdata["x"], bdata["y"])
        block_data.append({
            "uniqueId": bid,
            "type": bdata.get("type", 13),
            "pos": str(pos),
            "name": bdata.get("name", ""),
            "owner_uid": bdata.get("owner_uid", 0),
            "garrison": bdata.get("garrison", []),
        })

    data_items = [_data_item("svr_map_detail", {"blocks": block_data})]
    return _ok_response(data_items)


def handle_get_city_battle_report(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理战报查询"""
    report_id = param.get("id", "")
    reports = MOCK_DATA.get("battle_reports", {})
    report = reports.get(report_id)

    if not report:
        return _error_response(30113, f"report {report_id} not found")

    data_items = [_data_item("svr_battle_report", report)]
    return _ok_response(data_items)


def handle_op_self_set_gem(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理 GM 添加宝石"""
    player = _get_player(uid)
    if not player:
        return _error_response(30001, f"player {uid} not found")

    gem_num = param.get("gem_num", 116666)
    old_gem = player.get("gem", 0)
    player["gem"] = gem_num

    data_items = [_data_item("svr_gem_stat", {"gem": gem_num})]
    print(f"  [mock] add_gem uid={uid}: {old_gem} → {gem_num} (SET)")
    return _ok_response(data_items)


def handle_op_add_soldiers(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理 GM 添加士兵"""
    player = _get_player(uid)
    if not player:
        return _error_response(30001, f"player {uid} not found")

    soldier_id = param.get("soldier_id", 204)
    soldier_num = param.get("soldier_num", 1000000)

    soldiers = player.get("soldiers", [])
    found = False
    for s in soldiers:
        if s["id"] == soldier_id:
            old_val = s["value"]
            s["value"] += soldier_num
            print(f"  [mock] add_soldiers uid={uid}: id={soldier_id} {old_val} + {soldier_num} = {s['value']} (ADD)")
            found = True
            break
    if not found:
        soldiers.append({"id": soldier_id, "value": soldier_num})
        player["soldiers"] = soldiers
        print(f"  [mock] add_soldiers uid={uid}: id={soldier_id} 0 + {soldier_num} = {soldier_num} (new)")

    data_items = [
        _data_item("svr_soldier", {"list": player["soldiers"]}),
        _data_item("svr_camp_soldier_count", {"num": sum(s["value"] for s in player["soldiers"])}),
    ]
    return _ok_response(data_items)


def handle_op_self_add_clear_resource(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理 GM 添加资源"""
    player = _get_player(uid)
    if not player:
        return _error_response(30001, f"player {uid} not found")

    op_type = param.get("op_type", 0)
    print(f"  [mock] add_resource uid={uid} op_type={op_type}")

    # 简单模拟：op_type=0 表示添加资源
    data_items = [_data_item("svr_resource_op", {"op_type": op_type, "status": "ok"})]
    return _ok_response(data_items)


# ---------------------------------------------------------------------------
# 命令路由表
# ---------------------------------------------------------------------------

CMD_HANDLERS = {
    "login_get": handle_login_get,
    "game_server_login_get": handle_game_server_login_get,
    "fixed_move_city_new": handle_fixed_move_city_new,
    "dispatch_troop": handle_dispatch_troop,
    "dispatch_scout": handle_dispatch_scout,
    "create_rally_war": handle_create_rally_war,
    "recall_reinforce": handle_recall_reinforce,
    "change_troop": handle_change_troop,
    "get_map_brief_obj": handle_get_map_brief_obj,
    "game_svr_map_get": handle_game_svr_map_get,
    "get_city_battle_report": handle_get_city_battle_report,
    "op_self_set_gem": handle_op_self_set_gem,
    "op_add_soldiers": handle_op_add_soldiers,
    "op_self_add_clear_resource": handle_op_self_add_clear_resource,
}


# ---------------------------------------------------------------------------
# HTTP 端点
# ---------------------------------------------------------------------------


@app.get("/{path:path}")
async def handle_get_request(request: Request):
    """处理 GET 协议请求

    真实 test 服务器使用 GET {base_url}?{json_body} 格式。
    query string 就是整个 JSON body（URL 编码后）。
    """
    raw_qs = unquote(str(request.url.query))
    if not raw_qs:
        return JSONResponse({"error": "missing json body in query string"}, status_code=400)

    try:
        body = json.loads(raw_qs)
    except json.JSONDecodeError as e:
        return JSONResponse({"error": f"invalid json: {e}"}, status_code=400)

    uid = body.get("header", {}).get("uid", 0)
    cmd = body.get("request", {}).get("cmd", "")
    param = body.get("request", {}).get("param", {})

    handler = CMD_HANDLERS.get(cmd)
    if handler is None:
        return JSONResponse(
            _error_response(30001, f"unknown cmd: {cmd}"),
            status_code=200,
        )

    result = handler(uid, param)

    # 注入 request echo (与真实服务器一致)
    result["request"] = body

    return JSONResponse(result)


# ---------------------------------------------------------------------------
# 直接运行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    port = 18888
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    print(f"Mock server starting on http://localhost:{port}")
    print(f"Loaded {len(MOCK_DATA.get('players', {}))} players, {len(MOCK_DATA.get('buildings', {}))} buildings")
    uvicorn.run(app, host="0.0.0.0", port=port)
