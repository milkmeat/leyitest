#!/usr/bin/env python3
"""
MCP Server 启动脚本

直接在当前 Python 进程中运行 MCP server，避免 Windows 上 os.execv 的问题。
"""
import sys
from pathlib import Path

# 确保项目目录在 Python 路径中
script_dir = Path(__file__).parent.resolve()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

if __name__ == "__main__":
    import asyncio
    from phone_mcp_server import main
    asyncio.run(main())
