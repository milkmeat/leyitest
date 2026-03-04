import json
from typing import Dict, Any


class RequestBuilder:
    """请求构建器，负责构建完整的请求URL"""

    # 固定的extra_info参数
    EXTRA_INFO = {"no_checkac": 1, "op_cmd": 1}

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def build(self, header: Dict[str, Any], cmd: str, param: Dict[str, Any]) -> str:
        """
        构建完整请求URL

        Args:
            header: 请求头信息（每次调用时传入）
            cmd: 命令名称
            param: 命令参数

        Returns:
            完整的请求URL
        """
        # 构建完整的请求JSON对象
        request_body = {
            "header": header,
            "request": {
                "cmd": cmd,
                "param": param
            },
            "extra_info": self.EXTRA_INFO
        }

        # 将JSON对象序列化为字符串（不编码）
        json_str = json.dumps(request_body, separators=(',', ':'), ensure_ascii=False)
        return f"{self.base_url}?{json_str}"

    def build_readable(self, header: Dict[str, Any], cmd: str, param: Dict[str, Any]) -> str:
        """
        构建可读的URL（带缩进，仅用于调试显示）
        """
        request_body = {
            "header": header,
            "request": {
                "cmd": cmd,
                "param": param
            },
            "extra_info": self.EXTRA_INFO
        }
        json_str = json.dumps(request_body, separators=(',', ':'), ensure_ascii=False)
        return f"{self.base_url}?{json_str}"

    def set_base_url(self, base_url: str):
        """设置基础URL"""
        self.base_url = base_url.rstrip('/')
