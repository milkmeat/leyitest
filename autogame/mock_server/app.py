"""Mock 游戏服务器 — FastAPI 应用

兼容真实 test 服务器的 GET 协议:
  GET {base_url}?{json_body}

json_body 格式:
  {"header": {..., "uid": xxx}, "request": {"cmd": "xxx", "param": {...}}, "extra_info": {...}}

启动方式:
  cd mock_server && python app.py
  或: uvicorn mock_server.app:app --port 18888
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict
from urllib.parse import unquote

# 确保项目根目录在 sys.path 中
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import yaml
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.utils.coords import encode_pos

# ---------------------------------------------------------------------------
# 数据加载
# ---------------------------------------------------------------------------

MOCK_DATA_PATH = Path(__file__).resolve().parent / "mock_data.yaml"


def load_mock_data() -> Dict[str, Any]:
    with open(MOCK_DATA_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# 启动时加载一次
MOCK_DATA = load_mock_data()

app = FastAPI(title="WestGame Mock Server")


# ---------------------------------------------------------------------------
# 命令处理器
# ---------------------------------------------------------------------------


def handle_login_get(uid: int, param: Dict[str, Any]) -> Dict[str, Any]:
    """处理 login_get 命令 (get_player_pos 等)

    根据 param.list 中请求的数据名称返回对应数据。
    """
    requested = param.get("list", [])
    data_items = []

    if "svr_lord_info_new" in requested:
        player = MOCK_DATA.get("players", {}).get(uid)
        if player:
            city_pos = encode_pos(player["x"], player["y"])
            lord_data = {
                "lord_info_data": {
                    "lord_info": {
                        "city_pos": str(city_pos),
                        "name": player.get("name", ""),
                        "power": player.get("power", 0),
                    }
                }
            }
            data_items.append({
                "name": "svr_lord_info_new",
                "data": json.dumps(lord_data),
            })

    # 构造与真实服务器一致的嵌套响应格式
    return {
        "res_data": [
            {
                "push_list": [
                    {
                        "data": data_items,
                    }
                ]
            }
        ]
    }


# 命令路由表: cmd_string -> handler(uid, param) -> response_dict
CMD_HANDLERS = {
    "login_get": handle_login_get,
}


# ---------------------------------------------------------------------------
# HTTP 端点
# ---------------------------------------------------------------------------


@app.get("/{path:path}")
async def handle_get_request(request: Request):
    """处理 GET 协议请求

    真实 test 服务器使用 GET {base_url}?{json_body} 格式。
    query string 就是整个 JSON body（URL 编码后）。
    """
    # query string 是完整的 JSON（经 URL 编码）
    raw_qs = unquote(str(request.url.query))
    if not raw_qs:
        return JSONResponse({"error": "missing json body in query string"}, status_code=400)

    try:
        body = json.loads(raw_qs)
    except json.JSONDecodeError as e:
        return JSONResponse({"error": f"invalid json: {e}"}, status_code=400)

    uid = body.get("header", {}).get("uid", 0)
    cmd = body.get("request", {}).get("cmd", "")
    param = body.get("request", {}).get("param", {})

    handler = CMD_HANDLERS.get(cmd)
    if handler is None:
        return JSONResponse({"error": f"unknown cmd: {cmd}"}, status_code=400)

    result = handler(uid, param)
    return JSONResponse(result)


# ---------------------------------------------------------------------------
# 直接运行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    port = 18888
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    print(f"Mock server starting on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
