from typing import Dict, Any, Optional, List

from core.game_client import GameClient, GameResponse


# 命令描述映射
CMD_DESCRIPTIONS = {
    'add_gem': '添加宝石',
    'move_city': '移城',
    'add_soldiers': '添加士兵',
    'attack_city': '攻打玩家主城',
    'add_resource': '添加资源',
    'scout_player': '侦查玩家',
    'get_player_pos': '获取玩家地图坐标',
}


class GameActions:
    """游戏操作聚合类，封装常用操作组合，支持链式调用"""

    def __init__(self, env: Optional[str] = None):
        """
        初始化GameActions

        Args:
            env: 环境名称，为None时使用配置文件中的current_env
        """
        self.client = GameClient(env=env)
        self._pending_actions: List[Dict[str, Any]] = []

    def add_gem(self, header: Dict[str, Any], gem_num: int = 116666) -> 'GameActions':
        """
        添加宝石操作

        Args:
            header: 请求头信息
            gem_num: 宝石数量

        Returns:
            self，支持链式调用
        """
        self._pending_actions.append({
            'cmd_name': 'add_gem',
            'header': header,
            'param': {'gem_num': gem_num}
        })
        return self

    def move_city(self, header: Dict[str, Any], x: int, y: int) -> 'GameActions':
        """
        花费宝石移城操作（链式调用，需execute执行）

        Args:
            header: 请求头信息
            x: 目标X坐标
            y: 目标Y坐标

        Returns:
            self，支持链式调用
        """
        # 坐标转换: tar_pos = x * 100000000 + y * 100
        tar_pos = x * 100000000 + y * 100
        self._pending_actions.append({
            'cmd_name': 'move_city',
            'header': header,
            'param': {
                'use_gem': 1,
                'item_id': 1,
                'tar_pos': tar_pos
            },
            'description': f'移城到({x},{y})'
        })
        return self

    def move_city_now(self, header: Dict[str, Any], x: int, y: int) -> GameResponse:
        """
        立即执行移城操作（不走链式调用）

        Args:
            header: 请求头信息
            x: 目标X坐标
            y: 目标Y坐标

        Returns:
            GameResponse对象
        """
        tar_pos = x * 100000000 + y * 100
        response = self.client.send_cmd('move_city', header, {
            'use_gem': 1,
            'item_id': 1,
            'tar_pos': tar_pos
        })

        # 打印结果反馈
        uid = header.get('uid', 'unknown')
        if response.is_success:
            print(f"[移城成功] uid={uid} 已移城到坐标({x},{y})")
        else:
            print(f"[移城失败] uid={uid} 移城到坐标({x},{y})失败, 错误码={response.ret_code}")

        return response

    def add_soldiers(self, header: Dict[str, Any], soldier_id: int = 204, soldier_num: int = 1000000) -> 'GameActions':
        """
        添加士兵操作

        Args:
            header: 请求头信息
            soldier_id: 士兵ID
            soldier_num: 士兵数量

        Returns:
            self，支持链式调用
        """
        self._pending_actions.append({
            'cmd_name': 'add_soldiers',
            'header': header,
            'param': {
                'soldier_id': soldier_id,
                'soldier_num': soldier_num
            }
        })
        return self

    def attack_city(
        self,
        header: Dict[str, Any],
        target_uid: int,
        target_x: int,
        target_y: int,
        soldier_id: int = 204,
        soldier_num: int = 1800
    ) -> 'GameActions':
        """
        攻打玩家主城（不带英雄）

        Args:
            header: 请求头信息
            target_uid: 目标玩家UID
            target_x: 目标X坐标
            target_y: 目标Y坐标
            soldier_id: 士兵类型ID
            soldier_num: 士兵数量

        Returns:
            self，支持链式调用
        """
        # 坐标转换: pos = x * 100000000 + y * 100
        pos = str(target_x * 100000000 + target_y * 100)
        # ID转换: 2_uid_1
        target_id = f"2_{target_uid}_1"

        self._pending_actions.append({
            'cmd_name': 'attack_city',
            'header': header,
            'param': {
                'target_type': 2,
                'march_info': {
                    'hero': {'vice': {}},
                    'over_defend': False,
                    'leader': 1,
                    'soldier_total_num': soldier_num,
                    'heros': {},
                    'queue_id': 6001,
                    'soldier': {str(soldier_id): soldier_num},
                    'carry_lord': 1
                },
                'march_type': 2,
                'target_info': {
                    'pos': pos,
                    'id': target_id
                }
            }
        })
        return self

    def add_resource(self, header: Dict[str, Any], op_type: int = 0) -> 'GameActions':
        """
        添加各类资源（默认100w）

        Args:
            header: 请求头信息
            op_type: 操作类型（默认0）

        Returns:
            self，支持链式调用
        """
        self._pending_actions.append({
            'cmd_name': 'add_resource',
            'header': header,
            'param': {'op_type': op_type}
        })
        return self

    def scout_player(
        self,
        header: Dict[str, Any],
        target_uid: int,
        target_x: int,
        target_y: int
    ) -> 'GameActions':
        """
        侦查玩家

        Args:
            header: 请求头信息
            target_uid: 侦查目标UID
            target_x: 目标X坐标
            target_y: 目标Y坐标

        Returns:
            self，支持链式调用
        """
        # 坐标转换: tar_pos = x * 100000000 + y * 100
        tar_pos = target_x * 100000000 + target_y * 100
        # unique_id转换: 2_uid_1
        unique_id = f"2_{target_uid}_1"

        self._pending_actions.append({
            'cmd_name': 'scout_player',
            'header': header,
            'param': {
                'need_camp': 0,
                'scout_queue_id': 8001,
                'tar_info': {
                    'unique_id': unique_id,
                    'type': 2,
                    'id': target_uid,
                    'lv': 1,
                    'name': f"player_{target_uid}"
                },
                'tar_type': 5,
                'tar_limit': [],
                'tar_pos': tar_pos
            }
        })
        return self

    def get_player_pos(self, header: Dict[str, Any]) -> 'GameActions':
        """
        获取玩家地图坐标（链式调用，需execute执行）

        Args:
            header: 请求头信息

        Returns:
            self，支持链式调用
        """
        self._pending_actions.append({
            'cmd_name': 'get_player_pos',
            'header': header,
            'param': None
        })
        return self

    def get_player_pos_now(self, header: Dict[str, Any]) -> tuple:
        """
        立即获取玩家地图坐标

        Args:
            header: 请求头信息

        Returns:
            tuple: (city_pos, x, y, response) 原始坐标值、解析坐标和响应对象
                   失败时返回 (None, None, None, response)
        """
        response = self.client.send_cmd('get_player_pos', header, None)
        uid = header.get('uid', 'unknown')

        if response.is_success:
            # 从返回数据中提取pos信息
            city_pos = self._extract_city_pos_from_response(response)
            if city_pos:
                x, y = self.parse_pos(city_pos)
                print(f"[获取坐标成功] uid={uid} city_pos={city_pos} 坐标=({x},{y})")
                return (city_pos, x, y, response)
            else:
                print(f"[获取坐标失败] uid={uid} 未能从返回数据中解析坐标")
                return (None, None, None, response)
        else:
            print(f"[获取坐标失败] uid={uid} 错误码={response.ret_code}")
            return (None, None, None, response)

    @staticmethod
    def parse_pos(pos: int) -> tuple:
        """
        解析坐标值为 (x, y)

        坐标转换公式: pos = x * 100000000 + y * 100
        反向解析: x = pos // 100000000, y = (pos % 100000000) // 100

        Args:
            pos: 编码后的坐标值

        Returns:
            tuple: (x, y)
        """
        x = pos // 100000000
        y = (pos % 100000000) // 100
        return (x, y)

    def _extract_city_pos_from_response(self, response: GameResponse) -> Optional[int]:
        """
        从响应数据中提取玩家原始坐标值 city_pos

        数据结构: res_data[0].push_list[0].data[] -> 找到 name='svr_lord_info_new'
        然后解析 data 字段中的 lord_info_data.lord_info.city_pos

        Args:
            response: GameResponse对象

        Returns:
            int: 原始 city_pos 值，失败返回 None
        """
        import json as json_module
        try:
            res_data = response.res_data
            if not isinstance(res_data, list) or len(res_data) == 0:
                return None

            # 遍历 res_data[0].push_list[0].data[]
            push_list = res_data[0].get('push_list', [])
            if not push_list:
                return None

            data_list = push_list[0].get('data', [])
            for item in data_list:
                name = item.get('name', '')
                # 查找 svr_lord_info_new 或 svr_player
                if name == 'svr_lord_info_new':
                    data_str = item.get('data', '{}')
                    parsed = json_module.loads(data_str)
                    # 提取 lord_info_data.lord_info.city_pos
                    city_pos = parsed.get('lord_info_data', {}).get('lord_info', {}).get('city_pos')
                    if city_pos:
                        return int(city_pos)
                elif name == 'svr_player':
                    data_str = item.get('data', '{}')
                    parsed = json_module.loads(data_str)
                    # 提取 cid (城市位置)
                    cid = parsed.get('cid')
                    if cid:
                        return int(cid)
        except Exception as e:
            print(f"解析坐标异常: {e}")
        return None

    def custom_cmd(
        self,
        cmd_name: str,
        header: Dict[str, Any],
        param: Optional[Dict[str, Any]] = None
    ) -> 'GameActions':
        """
        添加自定义命令操作

        Args:
            cmd_name: 命令名称
            header: 请求头信息
            param: 命令参数

        Returns:
            self，支持链式调用
        """
        self._pending_actions.append({
            'cmd_name': cmd_name,
            'header': header,
            'param': param
        })
        return self

    def execute(self) -> List[GameResponse]:
        """
        执行所有待处理的操作，并打印每个操作的成功/失败反馈

        Returns:
            GameResponse对象列表
        """
        responses = []
        for action in self._pending_actions:
            cmd_name = action['cmd_name']
            header = action['header']
            uid = header.get('uid', 'unknown')

            response = self.client.send_cmd(
                cmd_name=cmd_name,
                header=header,
                param=action['param']
            )
            responses.append(response)

            # 打印结果反馈
            desc = action.get('description') or CMD_DESCRIPTIONS.get(cmd_name, cmd_name)
            if response.is_success:
                print(f"[成功] uid={uid} {desc}")
            else:
                print(f"[失败] uid={uid} {desc}, 错误码={response.ret_code}")

        # 清空待处理操作列表
        self._pending_actions.clear()
        return responses

    def preview(self) -> List[str]:
        """
        预览所有待处理操作的URL（不发送）

        Returns:
            URL列表
        """
        urls = []
        for action in self._pending_actions:
            url = self.client.build_url(
                cmd_name=action['cmd_name'],
                header=action['header'],
                param=action['param']
            )
            urls.append(url)
        return urls

    def clear(self) -> 'GameActions':
        """
        清空所有待处理的操作

        Returns:
            self，支持链式调用
        """
        self._pending_actions.clear()
        return self

    def switch_env(self, env_name: str) -> 'GameActions':
        """
        切换环境

        Args:
            env_name: 环境名称

        Returns:
            self，支持链式调用
        """
        self.client.switch_env(env_name)
        return self

    @property
    def pending_count(self) -> int:
        """获取待处理操作数量"""
        return len(self._pending_actions)

    def build_header(self, uid: int, sid: int = 1, aid: int = 0) -> Dict[str, Any]:
        """
        构建完整的请求头

        Args:
            uid: 用户ID（必填）
            sid: 服务器ID（默认1）
            aid: 联盟ID（默认0）

        Returns:
            完整的请求头字典
        """
        return self.client.build_header(uid, sid, aid)
