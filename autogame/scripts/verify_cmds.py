"""验证 cmd_config.yaml 中所有命令在 test 服务器上的可用性

用法: python scripts/verify_cmds.py [uid]
默认 uid: 20001946
"""

import asyncio
import json
import os
import sys

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.executor.game_api import GameAPIClient, CMD_CONFIG
from src.utils.coords import encode_pos


async def verify_all(uid: int):
    client = GameAPIClient(env="test")
    results = {}

    # 为每个命令构造安全的测试参数
    test_overrides = {
        "move_city": {"tar_pos": encode_pos(500, 500)},
        "attack_player": {
            "target_info": {"id": f"2_{uid}_1", "pos": str(encode_pos(500, 500))},
            "march_info": {"soldier": {"204": 1}, "hero": {"main": 21}},
        },
        "attack_building": {
            "target_info": {"id": "13_1001_1", "pos": str(encode_pos(500, 500))},
            "march_info": {"soldier": {"204": 1}, "hero": {"main": 21}},
        },
        "reinforce_building": {
            "target_info": {"id": "13_1001_1", "pos": str(encode_pos(500, 500))},
            "march_info": {"soldier": {"204": 1}, "hero": {"main": 21}},
        },
        "scout_player": {"tar_pos": encode_pos(500, 500)},
        "create_rally": {
            "target_info": {"id": f"2_{uid}_1"},
            "march_info": {"soldier": {"204": 1}, "hero": {"main": 21}},
        },
        "join_rally": {
            "target_info": {"id": "rally_test_id"},
            "march_info": {"soldier": {"204": 1}, "hero": {"main": 21}},
        },
        "recall_reinforce": {"unique_id": "test_id"},
        "recall_troop": {"march_info": {"ids": ["test_id"]}},
        "get_all_player_data": {},
        "get_player_info": {},
        "get_map_detail": {"sid": 0, "bid_list": [0]},
        "get_battle_report": {"id": "test_report_id"},
        "add_gem": {},
        "add_soldiers": {},
        "add_resource": {},
        "rally_dismiss": {"unique_id": "107_test_1"},
        "attack_city": {
            "target_info": {"id": f"2_{uid}_1", "pos": str(encode_pos(500, 500))},
        },
        "get_player_pos": {},
        "get_al_members": {},
        "copy_player": {
            "src_uid": uid, "src_sid": 1, "tar_uid": uid, "tar_sid": 1,
        },
        "change_name": {"name": f"test_{uid}"},
        "create_alliance": {"name": "TestAlliance", "nick": "TST"},
        "join_alliance": {"target_aid": 1},
        "al_leave": {},
        "al_help_all": {},
        "create_ava_battle": {"lvl_id": "test_battle_1"},
        "ava_add_player": {"lvl_id": "test_battle_1", "uid": uid, "camp_id": 1},
        "ava_enter_battle": {"lvl_id": "test_battle_1"},
    }

    # 协议字段名与 send_cmd 的 uid 参数冲突的命令，需要走 param_overrides
    uid_conflict_cmds = {"ava_add_player"}

    for cmd_name in CMD_CONFIG:
        overrides = test_overrides.get(cmd_name, {})
        try:
            if cmd_name in uid_conflict_cmds:
                resp = await client.send_cmd(cmd_name, uid, param_overrides=overrides)
            else:
                resp = await client.send_cmd(cmd_name, uid, **overrides)
            code = resp.get("code", "N/A")
            msg = resp.get("msg", "")
            # 检查是否有 res_data（查询类命令的正常响应）
            has_data = "res_data" in resp
            results[cmd_name] = {
                "status": "OK" if (code == 0 or has_data) else f"code={code}",
                "code": code,
                "msg": msg[:80] if msg else "",
                "has_data": has_data,
                "resp_keys": list(resp.keys())[:10],
            }
        except Exception as e:
            results[cmd_name] = {
                "status": "ERROR",
                "error": str(e)[:120],
            }

        # 打印实时进度
        r = results[cmd_name]
        status_str = r["status"]
        extra = r.get("msg", r.get("error", ""))
        print(f"  {cmd_name:30s} → {status_str:12s} {extra}")

    await client.close()

    print("\n===== 汇总 =====")
    ok_cmds = [k for k, v in results.items() if v["status"] == "OK"]
    fail_cmds = [k for k, v in results.items() if v["status"] != "OK"]
    print(f"可用 ({len(ok_cmds)}): {', '.join(ok_cmds)}")
    print(f"不可用 ({len(fail_cmds)}): {', '.join(fail_cmds)}")

    # 输出详细结果
    print("\n===== 详细结果 =====")
    print(json.dumps(results, indent=2, ensure_ascii=False))

    return results


if __name__ == "__main__":
    uid = int(sys.argv[1]) if len(sys.argv) > 1 else 20001946
    print(f"验证 test 服务器接口 (uid={uid})...\n")
    asyncio.run(verify_all(uid))
