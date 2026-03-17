"""pytest 全局配置 — marker 注册 + mock server fixture"""

import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: 集成测试 — 需要 mock server (deselect with: -m 'not integration')",
    )
    config.addinivalue_line(
        "markers",
        "slow: 慢速测试 — Windows 子进程开销大 (deselect with: -m 'not slow')",
    )


def _wait_for_port(port: int, host: str = "127.0.0.1", timeout: float = 10.0) -> bool:
    """等待端口可连接"""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


@pytest.fixture(scope="session")
def mock_server():
    """启动 mock server (localhost:18888)，测试结束后自动关闭

    仅在有 integration 标记的测试被选中时才会启动。
    """
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "mock_server.app:app",
         "--host", "127.0.0.1", "--port", "18888"],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if not _wait_for_port(18888):
        proc.terminate()
        stdout = proc.stdout.read().decode(errors="replace") if proc.stdout else ""
        stderr = proc.stderr.read().decode(errors="replace") if proc.stderr else ""
        pytest.fail(
            f"Mock server 未能在 10 秒内启动\nstdout: {stdout}\nstderr: {stderr}"
        )

    yield proc

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
