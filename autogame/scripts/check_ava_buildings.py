#!/usr/bin/env python3
"""检查 AVA 战场建筑信息"""
import sys
from pathlib import Path

# 自动将项目根目录加入 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import json
from src.executor.game_api import GameAPIClient

def decode_pos(pos_str):
    pos = int(pos_str)
    x = pos // 100000000
    y = (pos % 100000000) // 100
    return (x, y)

async def show_ava_buildings_detail():
    api = GameAPIClient(env='test')
    uid = 20010643

    try:
        result = await api.send_cmd('lvl_battle_login_get', uid, lvl_id=29999)

        if result['res_header']['ret_code'] == 0:
            for item in result['res_data']:
                for push in item.get('push_list', []):
                    for data in push.get('data', []):
                        if data['name'] == 'svr_lvl_brief_objs':
                            brief_data = json.loads(data['data'])
                            buildings = brief_data.get('briefObjs', [])

                            print('=== AVA 战场建筑列表 (lvl_id=29999) ===')
                            print(f'总共: {len(buildings)} 个对象\n')

                            # 阵营映射
                            camp_names = {0: '中立', 1: '阵营1(我方)', 2: '阵营2(敌方)'}

                            for b in buildings:
                                t = b['type']
                                pos = decode_pos(b['pos'])
                                camp = int(b.get('camp', 0))
                                key = b.get('key', 'N/A')

                                camp_name = camp_names.get(camp, f'阵营{camp}')

                                print(f'Type {t:5} | key:{key:>4} | pos:({pos[0]:>4},{pos[1]:>4}) | {camp_name:15} | {b["uniqueId"]}')

                                # 显示建筑额外信息
                                if t != 10101:
                                    fight_flag = b.get('fightFlag', 0)
                                    limit_troop = b.get('limitTroopNum', 0)
                                    if fight_flag > 0 or limit_troop > 0:
                                        print(f'  └─ 战斗标记:{fight_flag} 兵力上限:{limit_troop}')
                        elif data['name'] == 'svr_lvl_war_situation':
                            war_data = json.loads(data['data'])
                            print(f"\n=== 战场概况 ===")
                            print(f"地图ID: {war_data.get('mapId')}")
                            print(f"总建筑数: {war_data.get('totalLandBuildingNum')}")
                            print(f"开始时间: {war_data.get('avaStageInfo', {}).get('btime')}")
                            print(f"结束时间: {war_data.get('avaStageInfo', {}).get('etime')}")

                            print(f"\n=== 阵营信息 ===")
                            for camp in war_data.get('avaCampInfo', []):
                                camp_id = camp.get('campId')
                                aid = camp.get('aid')
                                al_nick = camp.get('alNick')
                                score = camp.get('score')
                                joiner_num = camp.get('joinerNum')
                                print(f"阵营{camp_id}: aid={aid}, nick={al_nick}, 积分={score}, 人数={joiner_num}")

        else:
            print(f'Error: {result}')

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
    finally:
        await api.close()

if __name__ == '__main__':
    asyncio.run(show_ava_buildings_detail())
