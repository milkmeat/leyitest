"""
游戏操作聚合类

职责：在 GameClient 基础上封装常用游戏操作，提供两种使用模式：

    模式1 — 链式调用 + 批量执行（适合批量操作场景）:
        actions = GameActions(env="test")
        header = actions.build_header(uid=20010366)
        actions.add_gem(header, 50000).add_soldiers(header).add_resource(header)
        responses = actions.execute()  # 一次性顺序执行所有操作

    模式2 — 立即执行（适合单个操作 + 需要即时结果）:
        actions = GameActions(env="test")
        header = actions.build_header(uid=20010366)
        city_pos, x, y, resp = actions.get_player_pos_now(header)

数据流（链式调用模式）:
    add_gem(header, 50000)  → 存入 _pending_actions 列表（不发送）
    add_soldiers(header)    → 存入 _pending_actions 列表（不发送）
    execute()               → 遍历列表，逐个调用 client.send_cmd() → 返回响应列表

数据流（立即执行模式）:
    get_player_pos_now(header) → 直接调用 client.send_cmd() → 解析响应 → 返回结果

数据流（自定义命令 — 用于 cmd_config.yaml 中已定义但未封装的命令）:
    actions.custom_cmd("change_name", header, {"name": "新名字"})
    actions.execute()
"""

import json
from typing import Dict, Any, Optional, List

from core.game_client import GameClient, GameResponse


class GameActions:
    """游戏操作聚合类 — 封装常用操作，支持链式调用和立即执行"""

    def __init__(self, env: Optional[str] = None):
        """
        Args:
            env: 环境名称（"dev"/"test"/"prod"），None 时使用配置文件默认值
        """
        self.client = GameClient(env=env)
        self._pending_actions: List[Dict[str, Any]] = []

    # ==================== 请求头构建 ====================

    def build_header(self, uid: int, sid: int = 1, aid: int = 0,
                     lvl_id: int = 0, battle_id: int = 0, battle_type: int = 0) -> Dict[str, Any]:
        """
        构建完整的请求头（委托给 GameClient）

        Args:
            uid:         用户ID（必填）
            sid:         服务器ID（默认1）
            aid:         联盟ID（默认0）
            lvl_id:      AVA战场ID（默认0）
            battle_id:   战场实例ID（默认0）
            battle_type: 战场类型（默认0）
        """
        return self.client.build_header(uid, sid, aid, lvl_id, battle_id, battle_type)

    # ==================== 链式操作（存入队列，execute 时执行）====================

    def add_gem(self, header: Dict[str, Any], gem_num: int = 116666) -> 'GameActions':
        """添加宝石（链式）"""
        self._pending_actions.append({
            'cmd_name': 'add_gem',
            'header': header,
            'param': {'gem_num': gem_num}
        })
        return self

    def move_city(self, header: Dict[str, Any], x: int, y: int) -> 'GameActions':
        """花费宝石移城（链式）— 坐标编码: pos = x * 1亿 + y * 100"""
        tar_pos = x * 100000000 + y * 100
        self._pending_actions.append({
            'cmd_name': 'move_city',
            'header': header,
            'param': {'use_gem': 1, 'item_id': 1, 'tar_pos': tar_pos},
            'description': f'移城到({x},{y})'
        })
        return self

    def add_soldiers(self, header: Dict[str, Any], soldier_id: int = 204,
                     soldier_num: int = 1000000) -> 'GameActions':
        """添加士兵（链式）— soldier_id: 204=T4步兵"""
        self._pending_actions.append({
            'cmd_name': 'add_soldiers',
            'header': header,
            'param': {'soldier_id': soldier_id, 'soldier_num': soldier_num}
        })
        return self

    def attack_city(self, header: Dict[str, Any], target_uid: int,
                    target_x: int, target_y: int,
                    soldier_id: int = 204, soldier_num: int = 1800) -> 'GameActions':
        """
        攻打玩家主城（链式，不带英雄）

        参数转换: pos = x*1亿+y*100, target_id = "2_{uid}_1"
        """
        pos = str(target_x * 100000000 + target_y * 100)
        self._pending_actions.append({
            'cmd_name': 'attack_city',
            'header': header,
            'param': {
                'target_type': 2,
                'march_info': {
                    'hero': {'vice': {}}, 'heros': {}, 'leader': 1,
                    'over_defend': False, 'carry_lord': 1,
                    'queue_id': 6001,
                    'soldier': {str(soldier_id): soldier_num},
                    'soldier_total_num': soldier_num,
                },
                'march_type': 2,
                'target_info': {'pos': pos, 'id': f"2_{target_uid}_1"}
            }
        })
        return self

    def add_resource(self, header: Dict[str, Any], op_type: int = 0) -> 'GameActions':
        """添加各类资源（链式）— op_type: 0=添加100w各类资源"""
        self._pending_actions.append({
            'cmd_name': 'add_resource',
            'header': header,
            'param': {'op_type': op_type}
        })
        return self

    def scout_player(self, header: Dict[str, Any], target_uid: int,
                     target_x: int, target_y: int) -> 'GameActions':
        """
        侦查玩家（链式）

        参数转换: tar_pos = x*1亿+y*100, unique_id = "2_{uid}_1"
        """
        tar_pos = target_x * 100000000 + target_y * 100
        self._pending_actions.append({
            'cmd_name': 'scout_player',
            'header': header,
            'param': {
                'need_camp': 0, 'scout_queue_id': 8001,
                'tar_type': 5, 'tar_limit': [],
                'tar_pos': tar_pos,
                'tar_info': {
                    'unique_id': f"2_{target_uid}_1",
                    'type': 2, 'id': target_uid,
                    'lv': 1, 'name': f"player_{target_uid}"
                },
            }
        })
        return self

    def get_player_pos(self, header: Dict[str, Any]) -> 'GameActions':
        """获取玩家地图坐标（链式）"""
        self._pending_actions.append({
            'cmd_name': 'get_player_pos',
            'header': header,
            'param': None
        })
        return self

    def custom_cmd(self, cmd_name: str, header: Dict[str, Any],
                   param: Optional[Dict[str, Any]] = None) -> 'GameActions':
        """
        添加自定义命令（链式）— 用于 cmd_config.yaml 中已定义但未封装的命令

        示例: actions.custom_cmd("change_name", header, {"name": "NewName"})
        """
        self._pending_actions.append({
            'cmd_name': cmd_name,
            'header': header,
            'param': param
        })
        return self

    # ==================== 批量执行/预览/清空 ====================

    def execute(self) -> List[GameResponse]:
        """
        顺序执行所有待处理操作并返回响应列表

        每个操作会打印成功/失败反馈，执行完毕后自动清空队列。
        """
        responses = []
        for action in self._pending_actions:
            cmd_name = action['cmd_name']
            header = action['header']
            uid = header.get('uid', 'unknown')

            response = self.client.send_cmd(cmd_name, header, action['param'])
            responses.append(response)

            # 打印反馈: 优先用 action 自定义描述，其次从配置读取
            desc = action.get('description') or self.client.config_loader.get_command_description(cmd_name) or cmd_name
            status = "成功" if response.is_success else f"失败, 错误码={response.ret_code}"
            print(f"[{status.split(',')[0]}] uid={uid} {desc}" +
                  (f", 错误码={response.ret_code}" if not response.is_success else ""))

        self._pending_actions.clear()
        return responses

    def preview(self) -> List[str]:
        """预览所有待处理操作的URL（不发送）"""
        return [
            self.client.build_url(a['cmd_name'], a['header'], a['param'])
            for a in self._pending_actions
        ]

    def clear(self) -> 'GameActions':
        """清空待处理队列"""
        self._pending_actions.clear()
        return self

    @property
    def pending_count(self) -> int:
        """待处理操作数量"""
        return len(self._pending_actions)

    # ==================== 立即执行操作 ====================

    def move_city_now(self, header: Dict[str, Any], x: int, y: int) -> GameResponse:
        """立即执行移城"""
        tar_pos = x * 100000000 + y * 100
        response = self.client.send_cmd('move_city', header, {
            'use_gem': 1, 'item_id': 1, 'tar_pos': tar_pos
        })
        uid = header.get('uid', 'unknown')
        status = "成功" if response.is_success else f"失败, 错误码={response.ret_code}"
        print(f"[移城{status.split(',')[0]}] uid={uid} 坐标({x},{y})")
        return response

    def get_player_pos_now(self, header: Dict[str, Any]) -> tuple:
        """
        立即获取玩家地图坐标

        Returns:
            (city_pos, x, y, response) — 失败时前三项为 None
        """
        response = self.client.send_cmd('get_player_pos', header, None)
        uid = header.get('uid', 'unknown')

        if not response.is_success:
            print(f"[获取坐标失败] uid={uid} 错误码={response.ret_code}")
            return (None, None, None, response)

        city_pos = self._extract_city_pos(response)
        if city_pos:
            x, y = self.parse_pos(city_pos)
            print(f"[获取坐标成功] uid={uid} city_pos={city_pos} 坐标=({x},{y})")
            return (city_pos, x, y, response)

        print(f"[获取坐标失败] uid={uid} 未能从返回数据中解析坐标")
        return (None, None, None, response)

    def get_lvl_map_objs_now(self, header: Dict[str, Any], x: int, y: int,
                              size: int = 10) -> List[Dict[str, Any]]:
        """
        立即获取AVA战场地块内容（以x,y为中心，size*size范围的bid）

        Args:
            header: 请求头（需包含lvl_id）
            x, y: 中心坐标
            size: 范围大小（默认10，即10x10=100个地块）

        Returns:
            地图对象列表，每项包含 bid, uniqueId, type, uid, pos 等信息；
            失败返回空列表
        """
        center_bx = x // 10 + 1
        center_by = y // 10 + 1
        half = size // 2

        bid_list = []
        for bx in range(center_bx - half, center_bx - half + size):
            for by in range(center_by - half, center_by - half + size):
                bid_list.append(bx * 1000 + by)

        response = self.client.send_cmd('lvl_svr_map_get', header, {'bid_list': bid_list})

        if not response.is_success:
            print(f"[获取地块失败] 错误码={response.ret_code}")
            return []

        # 解析 svr_lvl_map_objs
        try:
            data_list = response.res_data[0].get('push_list', [{}])[0].get('data', [])
            for item in data_list:
                if item.get('name') == 'svr_lvl_map_objs':
                    parsed = json.loads(item.get('data', '{}'))
                    map_objs = parsed.get('mapBidObjs', [])
                    # 统计
                    obj_count = sum(len(b.get('objs', [])) for b in map_objs)
                    empty_count = sum(1 for b in map_objs if not b.get('objs'))
                    print(f"[获取地块成功] 范围={size}x{size}, 有对象={obj_count}, 空地块={empty_count}")
                    self._print_map_objs_summary(map_objs)
                    return map_objs
        except Exception as e:
            print(f"[解析地块数据异常] {e}")

        print("[获取地块失败] 未找到 svr_lvl_map_objs")
        return []

    @staticmethod
    def _print_map_objs_summary(map_objs: List[Dict[str, Any]]):
        """格式化打印地图对象摘要"""
        type_names = {10101: '玩家城', 10001: '建筑', 101: '行军队伍'}
        for bid_info in map_objs:
            objs = bid_info.get('objs', [])
            if not objs:
                continue
            bid = bid_info['bid']
            for obj in objs:
                basic = obj.get('objBasic', {})
                obj_type = basic.get('type', 0)
                uid = basic.get('uid', '0')
                pos = basic.get('pos', '0')
                obj_id = basic.get('id', '')
                type_name = type_names.get(obj_type, f'type={obj_type}')

                detail = ''
                if obj_type == 10101:
                    city = obj.get('cityInfo', {})
                    detail = f" 等级={city.get('level', '?')} 兵力={city.get('curTroopNum', 0)} camp={basic.get('camp', '?')} {city.get('uname', '')}"
                elif obj_type == 10001:
                    bld = obj.get('building', {})
                    detail = f" 驻军={bld.get('curTroopNum', 0)} camp={basic.get('camp', '?')}"
                elif obj_type == 101:
                    march = obj.get('marchBasic', {})
                    detail = f" marchType={march.get('marchType', '?')}"

                print(f"  bid={bid} {type_name} uid={uid} pos={pos} id={obj_id}{detail}")

    def is_in_ava_battle(self, uid: int, sid: int = 1) -> tuple:
        """
        判断玩家是否处于AVA临时战场

        Returns:
            (is_in_battle, lvl_id, response)
        """
        header = self.build_header(uid=uid, sid=sid)
        response = self.client.send_cmd('get_player_lvl_info', header)

        if not response.is_success:
            print(f"[查询失败] uid={uid} 错误码={response.ret_code}")
            return (False, 0, response)

        try:
            for item in response.res_data[0]['push_list'][0]['data']:
                if item['name'] == 'svr_player_lvl_info':
                    parsed = json.loads(item['data'])
                    lvl_id = parsed.get('lvl_id', 0)
                    is_in = lvl_id != 0
                    status = f"AVA战场 lvl_id={lvl_id}" if is_in else "正常世界地图"
                    print(f"[查询成功] uid={uid} 当前在{status}")
                    return (is_in, lvl_id, response)
        except Exception as e:
            print(f"[解析异常] uid={uid} {e}")

        print(f"[查询失败] uid={uid} 未找到 svr_player_lvl_info 字段")
        return (False, 0, response)

    # ==================== 联盟操作 ====================

    def get_aid_by_uid(self, uid: int, sid: int) -> Optional[int]:
        """通过uid获取玩家所在联盟的aid"""
        header = self.build_header(uid=uid, sid=sid)
        response = self.client.send_cmd('get_player_info', header)

        if not response.is_success:
            print(f"[获取玩家信息失败] uid={uid} 错误码={response.ret_code}")
            return None

        # 从响应JSON中用正则快速提取 al_id
        import re
        result = re.search(r'"al_id":(\d+)', str(response.json_data))
        if result:
            aid = int(result.group(1))
            print(f"[获取aid成功] uid={uid} aid={aid}")
            return aid
        print(f"[获取aid失败] uid={uid} 未找到联盟信息")
        return None

    def get_alliance_uid_list(self, uid: int, sid: int, aid: int) -> List[int]:
        """获取联盟全部成员uid列表"""
        header = self.build_header(uid=uid, sid=sid, aid=aid)
        response = self.client.send_cmd('get_al_members', header, {})

        if not response.is_success:
            print(f"[获取联盟成员失败] aid={aid} 错误码={response.ret_code}")
            return []

        uid_list = []
        try:
            for item in response.res_data[0]['push_list'][0]['data']:
                if item['name'] == 'svr_al_member_list':
                    members = json.loads(item['data'])
                    uid_list = [m['profile']['uid'] for m in members['items']]
                    break
        except Exception as e:
            print(f"[解析联盟成员数据异常] {e}")

        print(f"[获取联盟成员成功] aid={aid} 共{len(uid_list)}人")
        return uid_list

    def create_alliance_with_members(self, sid: int, uid_list: List[int],
                                     name: str, nick: str, desc: str = "desc") -> Optional[int]:
        """
        创建联盟并批量加入成员（一条龙操作）

        uid_list[0] 为盟主（创建者），其余自动加入联盟。

        Returns:
            创建成功返回 aid，失败返回 None
        """
        if not uid_list:
            print("[创建联盟] uid_list为空")
            return None

        leader_uid = uid_list[0]
        members = uid_list[1:]

        # 第1步：创建联盟
        print("=" * 50)
        print(f"第1步：uid={leader_uid} 创建联盟 {name}({nick})")
        print("=" * 50)
        header = self.build_header(uid=leader_uid, sid=sid)
        resp = self.client.send_cmd('create_alliance', header, {
            'name': name, 'nick': nick, 'desc': desc
        })

        if not resp.is_success:
            print(f"[创建联盟失败] {resp.err_msg}")
            return None

        # 从返回数据中提取aid
        aid = self._extract_aid_from_create_response(resp)
        if aid is None:
            aid = self.get_aid_by_uid(uid=leader_uid, sid=sid)
        if aid is None:
            print("[创建联盟失败] 无法获取联盟aid")
            return None

        print(f"[创建联盟成功] aid={aid}")

        # 第2步：批量加入成员
        if members:
            print(f"\n{'=' * 50}")
            print(f"第2步：{len(members)}个玩家加入联盟 aid={aid}")
            print("=" * 50)
            success = fail = 0
            for uid in members:
                h = self.build_header(uid=uid, sid=sid)
                r = self.client.send_cmd('join_alliance', h, {'target_aid': aid})
                if r.is_success:
                    success += 1
                    print(f"  uid={uid} 加入成功")
                else:
                    fail += 1
                    print(f"  uid={uid} 加入失败: {r.err_msg}")

            print(f"\n{'=' * 50}")
            print(f"完成! 联盟 {name}({nick}) aid={aid}")
            print(f"总人数: {success + 1}人(含盟主), 失败: {fail}人")
            print("=" * 50)

        return aid

    # ==================== 环境切换 ====================

    def switch_env(self, env_name: str) -> 'GameActions':
        """切换运行环境"""
        self.client.switch_env(env_name)
        return self

    # ==================== 工具方法 ====================

    @staticmethod
    def parse_pos(pos: int) -> tuple:
        """
        解析编码坐标为 (x, y)

        编码规则: pos = x * 1亿 + y * 100
        示例: parse_pos(19200018900) → (192, 189)
        """
        x = pos // 100000000
        y = (pos % 100000000) // 100
        return (x, y)

    def _extract_city_pos(self, response: GameResponse) -> Optional[int]:
        """
        从 login_get 响应中提取玩家城市坐标

        响应数据结构:
            res_data[0].push_list[0].data[] →
                name="svr_lord_info_new" → data.lord_info_data.lord_info.city_pos
                name="svr_player"       → data.cid
        """
        try:
            data_list = response.res_data[0].get('push_list', [{}])[0].get('data', [])
            for item in data_list:
                name = item.get('name', '')
                if name == 'svr_lord_info_new':
                    parsed = json.loads(item.get('data', '{}'))
                    city_pos = parsed.get('lord_info_data', {}).get('lord_info', {}).get('city_pos')
                    if city_pos:
                        return int(city_pos)
                elif name == 'svr_player':
                    parsed = json.loads(item.get('data', '{}'))
                    cid = parsed.get('cid')
                    if cid:
                        return int(cid)
        except Exception as e:
            print(f"解析坐标异常: {e}")
        return None

    @staticmethod
    def _extract_aid_from_create_response(response: GameResponse) -> Optional[int]:
        """从创建联盟的返回数据中提取aid"""
        try:
            for push in response.res_data[0]['push_list'][0]['data']:
                if push['name'] == 'svr_alliance':
                    return json.loads(push['data']).get('aid')
        except Exception:
            pass
        return None
