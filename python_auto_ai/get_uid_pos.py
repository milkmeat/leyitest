"""
获取指定uid的坐标信息
"""

from core.game_client import GameClient
import json


def get_player_pos(uid):
    header = {
        "did": "self-system",
        "sid": 1,
        "uid": uid,
        "aid": 0,
        "ksid": 1,
        "ava_id": 0,
        "castle_lv": 25,
        "battle_type": 0,
        "battle_id": 0,
        "chat_scene": ",kingdom_1",
        "invoker_name": "evans_test_debug"
    }

    client = GameClient(env="test")
    response = client.send_cmd("get_player_pos", header, {})

    print(f"\nuid={uid} 完整响应JSON:")
    print(json.dumps(response.json_data, indent=2, ensure_ascii=False))

    return response


if __name__ == "__main__":
    get_player_pos(20001946)
