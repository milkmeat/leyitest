"""
功能测试脚本
22个玩家资源补充、随机一对一侦查和攻打
"""

import random
from actions.game_actions import GameActions


def test_22_players_battle():
    """
    测试22个玩家的资源补充、随机一对一侦查和攻打
    确保每个uid都发出了侦查和攻打
    """
    actions = GameActions(env="test")

    # 22个uid列表
    uids = [
        20010413, 20010414, 20010415, 20010416, 20010417,
        20010418, 20010419, 20010420, 20010421, 20010422,
        20010423, 20010424, 20010425, 20010426, 20010427,
        20010428, 20010429, 20010430, 20010431, 20010432,
        20010366, 20010373
    ]

    # ============================================================
    # 1. 获取所有玩家坐标
    # ============================================================
    print("=" * 60)
    print(f"1. 获取所有 {len(uids)} 个玩家坐标")
    print("=" * 60)

    players = {}  # {uid: {'header': header, 'city_pos': pos, 'x': x, 'y': y}}

    for uid in uids:
        header = actions.build_header(uid=uid)
        city_pos, x, y, _ = actions.get_player_pos_now(header)
        if city_pos:
            players[uid] = {
                'header': header,
                'city_pos': city_pos,
                'x': x,
                'y': y
            }
        else:
            print(f"[警告] uid={uid} 获取坐标失败，跳过该玩家")

    print(f"\n成功获取 {len(players)} 个玩家坐标")
    for uid, info in players.items():
        print(f"  uid={uid}: ({info['x']},{info['y']})")

    if len(players) < 2:
        print("有效玩家数量不足，终止测试")
        return

    # ============================================================
    # 2. 补充资源、宝石、兵力
    # ============================================================
    print("\n" + "=" * 60)
    print("2. 补充资源、宝石、兵力")
    print("=" * 60)

    for uid, info in players.items():
        header = info['header']
        actions.add_gem(header, 500000)
        actions.add_resource(header)
        actions.add_soldiers(header, soldier_id=204, soldier_num=100000)

    print(f"\n执行补充操作 (共{actions.pending_count}个)...")
    actions.execute()

    # ============================================================
    # 3. 随机一对一侦查（每个玩家随机选择一个目标）
    # ============================================================
    print("\n" + "=" * 60)
    print("3. 随机一对一侦查")
    print("=" * 60)

    player_uids = list(players.keys())
    scout_pairs = []

    for uid in player_uids:
        # 随机选择一个不同于自己的目标
        targets = [u for u in player_uids if u != uid]
        target_uid = random.choice(targets)
        scout_pairs.append((uid, target_uid))

        info = players[uid]
        target_info = players[target_uid]

        print(f"[侦查] uid={uid} -> uid={target_uid} ({target_info['x']},{target_info['y']})")
        actions.scout_player(
            info['header'],
            target_uid=target_uid,
            target_x=target_info['x'],
            target_y=target_info['y']
        )

    print(f"\n执行侦查操作 (共{actions.pending_count}个)...")
    actions.execute()

    # ============================================================
    # 4. 随机一对一攻打（每个玩家随机选择一个目标）
    # ============================================================
    print("\n" + "=" * 60)
    print("4. 随机一对一攻打")
    print("=" * 60)

    attack_pairs = []

    for uid in player_uids:
        # 随机选择一个不同于自己的目标
        targets = [u for u in player_uids if u != uid]
        target_uid = random.choice(targets)
        attack_pairs.append((uid, target_uid))

        info = players[uid]
        target_info = players[target_uid]

        print(f"[攻打] uid={uid} -> uid={target_uid} ({target_info['x']},{target_info['y']})")
        actions.attack_city(
            info['header'],
            target_uid=target_uid,
            target_x=target_info['x'],
            target_y=target_info['y'],
            soldier_id=204,
            soldier_num=5000
        )

    print(f"\n执行攻打操作 (共{actions.pending_count}个)...")
    actions.execute()

    # ============================================================
    # 5. 统计结果
    # ============================================================
    print("\n" + "=" * 60)
    print("5. 统计结果")
    print("=" * 60)

    # 统计侦查
    scout_sent = {uid: 0 for uid in player_uids}
    scout_received = {uid: 0 for uid in player_uids}
    for attacker, target in scout_pairs:
        scout_sent[attacker] += 1
        scout_received[target] += 1

    # 统计攻打
    attack_sent = {uid: 0 for uid in player_uids}
    attack_received = {uid: 0 for uid in player_uids}
    for attacker, target in attack_pairs:
        attack_sent[attacker] += 1
        attack_received[target] += 1

    print(f"\n{'uid':<12} {'发出侦查':<10} {'被侦查':<10} {'发出攻打':<10} {'被攻打':<10}")
    print("-" * 60)
    for uid in player_uids:
        print(f"{uid:<12} {scout_sent[uid]:<10} {scout_received[uid]:<10} {attack_sent[uid]:<10} {attack_received[uid]:<10}")

    print("\n" + "=" * 60)
    print("测试完成")
    print(f"总计: {len(players)} 个玩家")
    print(f"侦查: {len(scout_pairs)} 次")
    print(f"攻打: {len(attack_pairs)} 次")
    print("=" * 60)


if __name__ == "__main__":
    test_22_players_battle()
