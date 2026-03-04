import os
import yaml
from typing import Dict, Any, Optional


class ConfigLoader:
    """配置加载器，负责加载YAML配置文件"""

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        self.config_dir = config_dir
        self._env_config: Optional[Dict] = None
        self._cmd_config: Optional[Dict] = None
        self._header_config: Optional[Dict] = None

    def _load_yaml(self, filename: str) -> Dict:
        """加载YAML文件"""
        filepath = os.path.join(self.config_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @property
    def env_config(self) -> Dict:
        """获取环境配置"""
        if self._env_config is None:
            self._env_config = self._load_yaml('env_config.yaml')
        return self._env_config

    @property
    def cmd_config(self) -> Dict:
        """获取命令配置"""
        if self._cmd_config is None:
            self._cmd_config = self._load_yaml('cmd_config.yaml')
        return self._cmd_config

    @property
    def header_config(self) -> Dict:
        """获取请求头配置"""
        if self._header_config is None:
            self._header_config = self._load_yaml('header_config.yaml')
        return self._header_config

    def get_default_header(self) -> Dict:
        """获取默认请求头配置"""
        return self.header_config.get('default_header', {}).copy()

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
        header = self.get_default_header()
        header['uid'] = uid
        header['sid'] = sid
        header['aid'] = aid
        return header

    def get_current_env(self) -> str:
        """获取当前环境名称"""
        return self.env_config.get('current_env', 'test')

    def get_env_url(self, env_name: Optional[str] = None) -> str:
        """获取指定环境的URL，默认为当前环境"""
        if env_name is None:
            env_name = self.get_current_env()
        environments = self.env_config.get('environments', {})
        env_info = environments.get(env_name, {})
        return env_info.get('url', '')

    def get_env_info(self, env_name: Optional[str] = None) -> Dict:
        """获取指定环境的完整信息"""
        if env_name is None:
            env_name = self.get_current_env()
        environments = self.env_config.get('environments', {})
        return environments.get(env_name, {})

    def get_command(self, cmd_name: str) -> Dict[str, Any]:
        """获取命令配置"""
        commands = self.cmd_config.get('commands', {})
        return commands.get(cmd_name, {})

    def get_command_cmd(self, cmd_name: str) -> str:
        """获取命令的cmd值"""
        cmd_info = self.get_command(cmd_name)
        return cmd_info.get('cmd', '')

    def get_command_default_param(self, cmd_name: str) -> Dict:
        """获取命令的默认参数"""
        cmd_info = self.get_command(cmd_name)
        return cmd_info.get('default_param', {})

    def list_environments(self) -> list:
        """列出所有可用环境"""
        return list(self.env_config.get('environments', {}).keys())

    def list_commands(self) -> list:
        """列出所有可用命令"""
        return list(self.cmd_config.get('commands', {}).keys())
