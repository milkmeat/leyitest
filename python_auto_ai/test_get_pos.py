"""
测试获取玩家地图坐标功能
"""

from core.game_client import GameClient
from actions.game_actions import GameActions
import json


def main():
    # 定义header
    header = {
        "did": "self-system",
        "sid": 1,
        "uid": 20010366,
        "aid": 0,
        "ksid": 1,
        "ava_id": 0,
        "castle_lv": 25,
        "battle_type": 0,
        "battle_id": 0,
        "chat_scene": ",kingdom_1",
        "invoker_name": "evans_test_debug"
    }

    print("=" * 60)
    print("测试获取玩家地图坐标")
    print("=" * 60)

    # 方式1: 使用GameClient直接发送，查看完整返回数据
    client = GameClient(env="test")
    print(f"当前环境: {client.get_current_env_info()}")

    print("\n[方式1] 使用GameClient直接发送")
    response = client.send_cmd("get_player_pos", header, {})

    print(f"\n完整响应JSON (格式化):")
    print(json.dumps(response.json_data, indent=2, ensure_ascii=False))

    print(f"\nis_success: {response.is_success}")
    print(f"ret_code: {response.ret_code}")
    print(f"res_data: {response.res_data}")

    # 方式2: 使用GameActions立即执行
    print("\n" + "=" * 60)
    print("[方式2] 使用GameActions获取坐标")
    print("=" * 60)

    actions = GameActions(env="test")
    x, y, resp = actions.get_player_pos_now(header)

    if x is not None:
        print(f"\n解析结果: 玩家 uid={header['uid']} 坐标为 ({x}, {y})")
    else:
        print("\n未能解析坐标，请检查返回数据结构")


if __name__ == "__main__":
    main()
