"""Mock 环境集成测试 — 将 shell 脚本包装为 pytest 用例

所有测试通过 subprocess 调用已有的 test_*.sh 脚本（--mock 模式），
依赖 conftest.py 中的 mock_server fixture 自动启停 mock server。

运行方式:
    pytest tests/test_integration_mock.py -v          # 跑全部集成测试（含慢速）
    pytest -m integration -v                          # 按 marker 选择
    pytest -m "not integration"                       # 跳过集成测试，只跑单元测试
    pytest -m "not slow" -v                           # 跳过慢速测试（推荐日常回归）

性能说明:
    Windows 上每次 Python 子进程启动 ~3s，shell 脚本调用多次 CLI 导致:
    - test_l0_commands: ~163s（14次子进程）
    - test_data_sync:   ~48s（9次子进程）
    - test_l1_view:     ~14s（5次子进程）
    这 3 个 xfail 测试已额外标记 @pytest.mark.slow，默认回归时可跳过。

    test_solo.sh 和 test_rally.sh 未包含在 pytest 中，因为它们需要
    几十次 CLI 子进程调用，总耗时 3-5 分钟。请手动运行: bash test_solo.sh --mock
"""

import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------
# 辅助
# ------------------------------------------------------------------

def _run_shell_test(
    script_name: str,
    *extra_args: str,
    timeout: int = 120,
) -> subprocess.CompletedProcess:
    """执行项目根目录下的 shell 脚本并返回结果"""
    script_path = PROJECT_ROOT / script_name
    result = subprocess.run(
        ["bash", str(script_path), *extra_args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        timeout=timeout,
        env=None,  # 继承当前环境
    )
    return result


def _assert_script_passed(result: subprocess.CompletedProcess, script_name: str):
    """断言脚本以 exit 0 退出，失败时打印 stdout/stderr"""
    if result.returncode != 0:
        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        stdout_tail = "\n".join(stdout.splitlines()[-60:])
        stderr_tail = "\n".join(stderr.splitlines()[-20:])
        pytest.fail(
            f"{script_name} 退出码={result.returncode}\n"
            f"--- stdout (tail) ---\n{stdout_tail}\n"
            f"--- stderr (tail) ---\n{stderr_tail}"
        )


# ------------------------------------------------------------------
# 完全兼容 mock 的脚本（稳定通过）
# ------------------------------------------------------------------

@pytest.mark.integration
class TestMockCompatible:
    """这些脚本在 mock 环境下稳定通过"""

    def test_l1_decide_dry_run(self, mock_server):
        """L1 决策 dry-run — 指令生成 + JSON 结构 + 主循环"""
        result = _run_shell_test("test_l1.sh")
        _assert_script_passed(result, "test_l1.sh")

    def test_main_loop(self, mock_server):
        """主循环 — 单轮/多轮 + 阶段标记 + 日志"""
        result = _run_shell_test("test_loop.sh", "--mock")
        _assert_script_passed(result, "test_loop.sh --mock")

    def test_llm_dry_run(self, mock_server):
        """LLM dry-run 模式返回预设 JSON"""
        result = _run_shell_test("test_llm.sh")
        _assert_script_passed(result, "test_llm.sh")


# ------------------------------------------------------------------
# Mock 数据不完全兼容的脚本（标记 xfail，完善 mock 后会自动 XPASS）
# ------------------------------------------------------------------

_MOCK_UID_MISMATCH = "mock_data.yaml UID 与脚本/config 中的 UID 不匹配"

@pytest.mark.integration
@pytest.mark.slow
class TestMockPartial:
    """这些脚本在 mock 模式下可运行但部分 check 会失败

    当 mock_data.yaml 补全所需 UID 后，xfail 会变为 XPASS。
    标记 @slow — 这3个测试共耗时 ~225s，日常回归可跳过: pytest -m "not slow"
    """

    @pytest.mark.xfail(reason=_MOCK_UID_MISMATCH, strict=False)
    def test_l1_view(self, mock_server):
        """L1 局部视图 — sync 查不到 squad 成员"""
        result = _run_shell_test("test_l1_view.sh")
        _assert_script_passed(result, "test_l1_view.sh")

    @pytest.mark.xfail(reason=_MOCK_UID_MISMATCH, strict=False)
    def test_data_sync(self, mock_server):
        """数据同步 — 单账号 sync 找不到 UID"""
        result = _run_shell_test("test_sync.sh", "--mock")
        _assert_script_passed(result, "test_sync.sh --mock")

    @pytest.mark.xfail(reason=_MOCK_UID_MISMATCH, strict=False)
    def test_l0_commands(self, mock_server):
        """L0 命令 — add_gem/soldiers/resource + MOVE_CITY"""
        result = _run_shell_test("test_l0.sh", "--mock", timeout=180)
        _assert_script_passed(result, "test_l0.sh --mock")
