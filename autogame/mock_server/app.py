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


def _get_or_create_player(uid: int) -> Dict[str, Any]:
    """获取玩家，不存在时自动创建（用于 GM 命令）"""
    player = _get_player(uid)
    if player is None:
        import random
        player = {
            "name": f"player_{uid}",
            "x": random.randint(100, 900),
            "y": random.randint(100, 900),
            "gem": 0,
            "soldiers": [],
            "troops": [],
            "alliance_id": 0,
            "city_level": 25,
        }
        MOCK_DATA.setdefault("players", {})[uid] = player
        print(f"  [mock] auto-created player uid={uid} at ({player['x']},{player['y']})")
    return player


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
    player = _get_or_create_player(uid)

    gem_num = param.get("gem_num", 116666)
    old_gem = player.get("gem", 0)
    player["gem"] = gem_num

    data_items = [_data_item("svr_gem_stat", {"gem": gem_num})]
    print(f"  [mock] add_gem uid={uid}: {old_gem} → {gem_num} (SET)")
    return _ok_response(data_items)


def handle_op_add_soldiers(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理 GM 添加士兵"""
    player = _get_or_create_player(uid)

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
    player = _get_or_create_player(uid)

    op_type = param.get("op_type", 0)
    print(f"  [mock] add_resource uid={uid} op_type={op_type}")

    # 简单模拟：op_type=0 表示添加资源
    data_items = [_data_item("svr_resource_op", {"op_type": op_type, "status": "ok"})]
    return _ok_response(data_items)


def handle_op_copy_player(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理 GM 复制账号数据"""
    src_uid = param.get("src_uid", 0)
    tar_uid = param.get("tar_uid", 0)
    src_sid = param.get("src_sid", 0)
    tar_sid = param.get("tar_sid", 0)
    ignores = param.get("ignores", [])

    src_player = _get_player(src_uid)
    if not src_player:
        return _error_response(30001, f"source player {src_uid} not found")

    # 深拷贝源玩家数据到目标
    tar_player = deepcopy(src_player)
    tar_player["name"] = f"copy_{tar_uid}"
    MOCK_DATA.setdefault("players", {})[tar_uid] = tar_player

    data_items = [_data_item("svr_copy_result", {
        "src_uid": src_uid, "tar_uid": tar_uid, "status": "ok",
    })]
    print(f"  [mock] copy_player src={src_uid}(sid={src_sid}) → tar={tar_uid}(sid={tar_sid}) ignores={ignores}")
    return _ok_response(data_items)


def handle_player_name_change(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理改昵称"""
    player = _get_or_create_player(uid)
    new_name = param.get("name", "")
    old_name = player.get("name", "")
    player["name"] = new_name

    data_items = [_data_item("svr_name_change", {"name": new_name, "status": "ok"})]
    print(f"  [mock] change_name uid={uid}: '{old_name}' → '{new_name}'")
    return _ok_response(data_items)


def handle_al_create(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理创建联盟"""
    name = param.get("name", "")
    nick = param.get("nick", "")
    alliance_id = int(time.time()) % 100000 + 10000

    alliance = {
        "aid": alliance_id,
        "name": name,
        "nick": nick,
        "leader_uid": uid,
        "members": [uid],
        "desc": param.get("desc", ""),
    }
    MOCK_DATA.setdefault("alliances", {})[alliance_id] = alliance

    # 更新玩家的联盟信息
    player = _get_or_create_player(uid)
    player["alliance_id"] = alliance_id
    player["alliance"] = name

    data_items = [_data_item("svr_alliance_create", {
        "aid": alliance_id, "name": name, "nick": nick,
    })]
    print(f"  [mock] create_alliance uid={uid} aid={alliance_id} name='{name}' nick='{nick}'")
    return _ok_response(data_items)


def handle_al_request_join(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理加入联盟"""
    target_aid = param.get("target_aid", 0)

    alliances = MOCK_DATA.get("alliances", {})
    alliance = alliances.get(target_aid)

    player = _get_or_create_player(uid)
    # 模拟自动通过
    player["alliance_id"] = target_aid
    if alliance:
        alliance.setdefault("members", []).append(uid)
        player["alliance"] = alliance.get("name", "")

    data_items = [_data_item("svr_alliance_join", {
        "aid": target_aid, "status": "joined",
    })]
    print(f"  [mock] join_alliance uid={uid} target_aid={target_aid}")
    return _ok_response(data_items)


def handle_get_self_al_member(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理获取联盟成员列表"""
    player = _get_player(uid)
    aid = player.get("alliance_id", 0) if player else 0

    members = []
    alliances = MOCK_DATA.get("alliances", {})
    alliance = alliances.get(aid)
    if alliance:
        for member_uid in alliance.get("members", []):
            m_player = _get_player(member_uid)
            members.append({
                "uid": member_uid,
                "name": m_player.get("name", "") if m_player else f"player_{member_uid}",
                "level": m_player.get("lord_level", 1) if m_player else 1,
            })
    else:
        # 没有联盟数据时，返回同 alliance_id 的所有玩家
        for pid, pdata in MOCK_DATA.get("players", {}).items():
            if pdata.get("alliance_id") == aid and aid != 0:
                members.append({
                    "uid": pid,
                    "name": pdata.get("name", ""),
                    "level": pdata.get("lord_level", 1),
                })

    data_items = [_data_item("svr_al_members", {"list": members, "count": len(members)})]
    print(f"  [mock] get_al_members uid={uid} aid={aid} count={len(members)}")
    return _ok_response(data_items)


def handle_al_leave(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理离开联盟"""
    player = _get_or_create_player(uid)
    old_aid = player.get("alliance_id", 0)
    player["alliance_id"] = 0
    player["alliance"] = ""

    # 从联盟成员列表中移除
    alliances = MOCK_DATA.get("alliances", {})
    alliance = alliances.get(old_aid)
    if alliance:
        members = alliance.get("members", [])
        if uid in members:
            members.remove(uid)

    data_items = [_data_item("svr_al_leave", {"aid": old_aid, "status": "left"})]
    print(f"  [mock] al_leave uid={uid} old_aid={old_aid}")
    return _ok_response(data_items)


def handle_al_help_all(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理一键帮助盟友"""
    data_items = [_data_item("svr_al_help", {"helped_count": 0, "status": "ok"})]
    print(f"  [mock] al_help_all uid={uid}")
    return _ok_response(data_items)


def handle_rally_dismiss(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理队长解散集结"""
    unique_id = param.get("unique_id", "")
    rallies = MOCK_DATA.get("rallies", {})

    # 尝试通过 unique_id 找到集结
    found = False
    for rally_id, rally in list(rallies.items()):
        if rally.get("creator_uid") == uid or rally_id == unique_id:
            del rallies[rally_id]
            found = True
            print(f"  [mock] rally_dismiss uid={uid} rally_id={rally_id}")
            break

    if not found:
        print(f"  [mock] rally_dismiss uid={uid} unique_id={unique_id} (not found, ignored)")

    data_items = [_data_item("svr_rally_dismiss", {"unique_id": unique_id, "status": "dismissed"})]
    return _ok_response(data_items)


def handle_op_create_lvl_battle(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理创建 AVA 临时战场"""
    battle_id = param.get("lvl_id", str(int(time.time())))
    event_id = param.get("event_id", "123456")
    camp = param.get("camp", [])

    battle = {
        "lvl_id": battle_id,
        "event_id": event_id,
        "camp": camp,
        "create_time": int(time.time()),
        "status": "created",
        "players": {},
    }
    # 从 camp 配置中预填充玩家
    for c in camp:
        camp_id = c.get("al_flag", 0)
        for member_uid in c.get("uid_list", []):
            battle["players"][member_uid] = {"camp_id": camp_id, "entered": False}

    MOCK_DATA.setdefault("ava_battles", {})[battle_id] = battle

    data_items = [_data_item("svr_lvl_battle_create", {
        "lvl_id": battle_id, "event_id": event_id, "status": "created",
    })]
    print(f"  [mock] create_ava_battle uid={uid} lvl_id={battle_id} camps={len(camp)}")
    return _ok_response(data_items)


def handle_op_lvl_set_player(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理添加玩家到 AVA 战场"""
    lvl_id = param.get("lvl_id", "")
    target_uid = param.get("uid", 0)
    camp_id = param.get("camp_id", 1)

    battles = MOCK_DATA.get("ava_battles", {})
    battle = battles.get(lvl_id)
    if not battle:
        return _error_response(30001, f"battle {lvl_id} not found")

    battle["players"][target_uid] = {"camp_id": camp_id, "entered": False}

    data_items = [_data_item("svr_lvl_set_player", {
        "lvl_id": lvl_id, "uid": target_uid, "camp_id": camp_id,
    })]
    print(f"  [mock] ava_add_player lvl_id={lvl_id} uid={target_uid} camp={camp_id}")
    return _ok_response(data_items)


def handle_op_enter_lvl_battle(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理进入 AVA 战场"""
    lvl_id = param.get("lvl_id", "")

    battles = MOCK_DATA.get("ava_battles", {})
    battle = battles.get(lvl_id)
    if not battle:
        return _error_response(30001, f"battle {lvl_id} not found")

    player_info = battle["players"].get(uid)
    if player_info:
        player_info["entered"] = True

    data_items = [_data_item("svr_lvl_enter", {
        "lvl_id": lvl_id, "uid": uid, "status": "entered",
    })]
    print(f"  [mock] ava_enter_battle uid={uid} lvl_id={lvl_id}")
    return _ok_response(data_items)


# ---------------------------------------------------------------------------
# 命令路由表
# ---------------------------------------------------------------------------

CMD_HANDLERS = {
    # 感知查询
    "login_get": handle_login_get,
    "game_server_login_get": handle_game_server_login_get,
    "game_svr_map_get": handle_game_svr_map_get,
    "get_city_battle_report": handle_get_city_battle_report,
    "get_self_al_member": handle_get_self_al_member,
    # 行动指令
    "fixed_move_city_new": handle_fixed_move_city_new,
    "dispatch_troop": handle_dispatch_troop,
    "dispatch_scout": handle_dispatch_scout,
    "create_rally_war": handle_create_rally_war,
    "rally_dismiss": handle_rally_dismiss,
    "recall_reinforce": handle_recall_reinforce,
    "change_troop": handle_change_troop,
    # GM 指令
    "op_self_set_gem": handle_op_self_set_gem,
    "op_add_soldiers": handle_op_add_soldiers,
    "op_self_add_clear_resource": handle_op_self_add_clear_resource,
    "op_copy_player": handle_op_copy_player,
    "player_name_change": handle_player_name_change,
    # 联盟操作
    "al_create": handle_al_create,
    "al_request_join": handle_al_request_join,
    "al_leave": handle_al_leave,
    "al_help_all": handle_al_help_all,
    # AVA 战场
    "op_create_lvl_battle": handle_op_create_lvl_battle,
    "op_lvl_set_player": handle_op_lvl_set_player,
    "op_enter_lvl_battle": handle_op_enter_lvl_battle,
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
