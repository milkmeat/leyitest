#!/usr/bin/env python3
"""
生成 .mcp.json 配置文件

运行此脚本自动生成适合当前环境的 MCP 配置。
支持夜神模拟器、BlueStacks 等多种模拟器。
"""
import json
import sys
from pathlib import Path


def find_venv_python():
    """查找虚拟环境的 Python 解释器"""
    script_dir = Path(__file__).parent.resolve()

    venv_paths = [
        script_dir / ".venv",
        script_dir / "venv",
        script_dir / "env",
    ]

    for venv_path in venv_paths:
        if not venv_path.exists():
            continue

        # Windows
        win_python = venv_path / "Scripts" / "python.exe"
        if win_python.exists():
            return win_python.resolve()

        # Unix
        unix_python = venv_path / "bin" / "python"
        if unix_python.exists():
            return unix_python.resolve()

    return Path(sys.executable).resolve()


def find_adb_path():
    """查找 ADB 可执行文件路径"""
    script_dir = Path(__file__).parent.resolve()

    # 夜神模拟器
    nox_adb = Path("C:/Program Files/Nox/bin/adb.exe")
    if nox_adb.exists():
        return nox_adb

    # 夜神模拟器（Program Files x86）
    nox_adb_x86 = Path("C:/Program Files (x86)/Nox/bin/adb.exe")
    if nox_adb_x86.exists():
        return nox_adb_x86

    # BlueStacks
    bluestacks_adb = Path("C:/Program Files/BlueStacks_bgp64HD/HD-Adb.exe")
    if bluestacks_adb.exists():
        return bluestacks_adb

    # 其他常见位置
    android_sdk = Path.home() / "AppData" / "Local" / "Android" / "Sdk" / "platform-tools" / "adb.exe"
    if android_sdk.exists():
        return android_sdk

    return None


def detect_emulator():
    """检测模拟器类型"""
    # 检查夜神模拟器
    if (Path("C:/Program Files/Nox/bin/adb.exe").exists() or
        Path("C:/Program Files (x86)/Nox/bin/adb.exe").exists()):
        return "nox", "127.0.0.1:62001", "C:\\Program Files\\Nox\\bin\\adb.exe"

    # 检查 BlueStacks
    if Path("C:/Program Files/BlueStacks_bgp64HD/HD-Adb.exe").exists():
        return "bluestacks", "localhost:5555", "C:\\Program Files\\BlueStacks_bgp64HD\\HD-Adb.exe"

    return None, None, None


def main():
    script_dir = Path(__file__).parent.resolve()
    mcp_config = script_dir / ".mcp.json"

    # 检测模拟器
    emulator_type, device_id, adb_path = detect_emulator()

    if emulator_type:
        print(f"检测到模拟器: {emulator_type}")
        print(f"设备 ID: {device_id}")
        print(f"ADB 路径: {adb_path}")
        print()

        # 使用批处理启动脚本（Windows）
        config = {
            "mcpServers": {
                "phone-agent": {
                    "type": "stdio",
                    "command": "cmd",
                    "args": ["/c", "start_mcp_nox.bat"]
                }
            }
        }
    else:
        # 未检测到模拟器，使用默认 Python 方式
        python_path = find_venv_python()
        python_str = str(python_path).replace("\\", "/")
        server_str = str(script_dir / "phone_mcp_server.py").replace("\\", "/")

        config = {
            "mcpServers": {
                "phone-agent": {
                    "type": "stdio",
                    "command": python_str,
                    "args": [server_str]
                }
            }
        }

    with open(mcp_config, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"已生成配置文件: {mcp_config}")
    print()
    print("下一步:")
    print("1. 确保夜神模拟器已启动")
    print("2. 重启 Claude Code 以应用配置")
    print("3. 使用 /phone 命令开始自动化任务")


if __name__ == "__main__":
    main()
