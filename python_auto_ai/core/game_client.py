import requests
from typing import Dict, Any, Optional, List

from .config_loader import ConfigLoader
from .request_builder import RequestBuilder


class GameResponse:
    """游戏响应封装类"""

    def __init__(self, response: requests.Response):
        self.response = response
        self.status_code = response.status_code
        self._json_data = None

    @property
    def json_data(self) -> Dict:
        """获取JSON响应数据"""
        if self._json_data is None:
            try:
                self._json_data = self.response.json()
            except:
                self._json_data = {}
        return self._json_data

    @property
    def ret_code(self) -> int:
        """获取业务返回码"""
        return self.json_data.get('res_header', {}).get('ret_code', -1)

    @property
    def err_msg(self) -> str:
        """获取错误信息"""
        return self.json_data.get('res_header', {}).get('err_msg', '')

    @property
    def is_success(self) -> bool:
        """判断请求是否成功（ret_code == 0）"""
        return self.ret_code == 0

    @property
    def res_header(self) -> Dict:
        """获取响应头"""
        return self.json_data.get('res_header', {})

    @property
    def res_data(self) -> List:
        """获取响应数据"""
        return self.json_data.get('res_data', [])

    def __str__(self) -> str:
        status = "成功" if self.is_success else "失败"
        return f"[{status}] ret_code={self.ret_code}, err_msg={self.err_msg}"


class GameClient:
    """游戏HTTP客户端（同步）"""

    def __init__(self, env: Optional[str] = None, timeout: int = 30):
        """
        初始化游戏客户端

        Args:
            env: 环境名称，为None时使用配置文件中的current_env
            timeout: 请求超时时间（秒）
        """
        self.config_loader = ConfigLoader()
        self.current_env = env or self.config_loader.get_current_env()
        self.timeout = timeout

        base_url = self.config_loader.get_env_url(self.current_env)
        self.request_builder = RequestBuilder(base_url)

    def switch_env(self, env_name: str):
        """
        切换环境

        Args:
            env_name: 环境名称（dev/test/prod）
        """
        available_envs = self.config_loader.list_environments()
        if env_name not in available_envs:
            raise ValueError(f"环境 '{env_name}' 不存在，可用环境: {available_envs}")

        self.current_env = env_name
        base_url = self.config_loader.get_env_url(env_name)
        self.request_builder.set_base_url(base_url)
        print(f"已切换到环境: {env_name} ({self.config_loader.get_env_info(env_name).get('name', '')})")

    def send(self, url: str) -> requests.Response:
        """
        发送单个请求

        Args:
            url: 完整的请求URL

        Returns:
            响应对象
        """
        response = requests.get(url, timeout=self.timeout)
        return response

    def send_batch(self, urls: List[str]) -> List[requests.Response]:
        """
        顺序发送多个请求

        Args:
            urls: 请求URL列表

        Returns:
            响应对象列表
        """
        responses = []
        for url in urls:
            response = self.send(url)
            responses.append(response)
        return responses

    def send_cmd(
        self,
        cmd_name: str,
        header: Dict[str, Any],
        param: Optional[Dict[str, Any]] = None
    ) -> GameResponse:
        """
        发送命令请求

        Args:
            cmd_name: 命令名称（如 add_gem, move_city）
            header: 请求头信息
            param: 命令参数，为None时使用默认参数

        Returns:
            GameResponse对象，包含is_success、ret_code等属性
        """
        cmd = self.config_loader.get_command_cmd(cmd_name)
        if not cmd:
            raise ValueError(f"命令 '{cmd_name}' 不存在")

        if param is None:
            param = self.config_loader.get_command_default_param(cmd_name)

        url = self.request_builder.build(header, cmd, param)
        print(f"发送请求: {cmd_name}")
        print(f"URL: {url}")

        response = self.send(url)
        game_response = GameResponse(response)
        print(f"响应状态: {game_response}")
        return game_response

    def build_url(
        self,
        cmd_name: str,
        header: Dict[str, Any],
        param: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        构建请求URL（不发送，用于预览）

        Args:
            cmd_name: 命令名称
            header: 请求头信息
            param: 命令参数

        Returns:
            请求URL
        """
        cmd = self.config_loader.get_command_cmd(cmd_name)
        if not cmd:
            raise ValueError(f"命令 '{cmd_name}' 不存在")

        if param is None:
            param = self.config_loader.get_command_default_param(cmd_name)

        return self.request_builder.build(header, cmd, param)

    def get_current_env_info(self) -> Dict:
        """获取当前环境信息"""
        return {
            'env_name': self.current_env,
            'env_info': self.config_loader.get_env_info(self.current_env)
        }

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
        return self.config_loader.build_header(uid, sid, aid)
