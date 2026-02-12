"""Task tracking system for phone automation sessions.

This module provides task session management, screenshot saving,
and report generation for phone automation tasks.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class TaskStep:
    """A single step in a task execution."""

    step_number: int
    timestamp: str
    screenshot_before: str | None = None
    screenshot_after: str | None = None
    current_app: str = ""
    claude_analysis: str = ""
    claude_decision: str = ""
    action: dict = field(default_factory=dict)
    autoglm_response: dict = field(default_factory=dict)
    result: dict = field(default_factory=dict)


@dataclass
class TaskSession:
    """A task session containing metadata and steps."""

    task_id: str
    task_dir: Path
    user_request: str
    created_at: str
    status: str = "running"
    completed_at: str | None = None
    steps: list[TaskStep] = field(default_factory=list)
    device: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert session to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "task_dir": str(self.task_dir),
            "user_request": self.user_request,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "device": self.device,
            "steps": [asdict(step) for step in self.steps],
        }


class TaskTracker:
    """
    Task tracker for managing phone automation sessions.

    Handles:
    - Creating and managing task sessions
    - Saving screenshots to task directories
    - Recording execution steps
    - Generating JSON data and Markdown reports
    """

    BASE_DIR = Path("phone-agent-tasks")

    def __init__(self, base_dir: Path | str | None = None):
        """
        Initialize the task tracker.

        Args:
            base_dir: Optional custom base directory for task storage.
        """
        if base_dir:
            self.BASE_DIR = Path(base_dir)
        self.BASE_DIR.mkdir(exist_ok=True)
        self._sessions: dict[str, TaskSession] = {}

    def create_session(self, user_request: str, device_info: dict | None = None) -> TaskSession:
        """
        Create a new task session.

        Args:
            user_request: The user's original request.
            device_info: Optional device information dict.

        Returns:
            The created TaskSession.
        """
        task_id = self._generate_task_id()
        task_dir = self.BASE_DIR / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "screenshots").mkdir(exist_ok=True)

        session = TaskSession(
            task_id=task_id,
            task_dir=task_dir,
            user_request=user_request,
            created_at=datetime.now().isoformat(),
            device=device_info or {},
        )
        self._sessions[task_id] = session
        return session

    def get_session(self, task_id: str) -> TaskSession | None:
        """Get a session by task ID."""
        return self._sessions.get(task_id)

    def save_screenshot(
        self,
        task_id: str,
        step_number: int,
        timing: str,
        data: bytes
    ) -> str:
        """
        Save a screenshot to the task directory.

        Args:
            task_id: The task session ID.
            step_number: The step number (1-indexed).
            timing: Either "before" or "after".
            data: Raw PNG image bytes.

        Returns:
            Relative path to the saved screenshot.
        """
        session = self._sessions.get(task_id)
        if not session:
            raise ValueError(f"Session not found: {task_id}")

        filename = f"step_{step_number:03d}_{timing}.png"
        filepath = session.task_dir / "screenshots" / filename
        filepath.write_bytes(data)
        return f"screenshots/{filename}"

    def add_step(self, task_id: str, step: TaskStep) -> None:
        """
        Add an execution step to the session.

        Args:
            task_id: The task session ID.
            step: The TaskStep to add.
        """
        session = self._sessions.get(task_id)
        if not session:
            raise ValueError(f"Session not found: {task_id}")
        session.steps.append(step)

    def update_step(
        self,
        task_id: str,
        step_number: int,
        **updates
    ) -> None:
        """
        Update an existing step.

        Args:
            task_id: The task session ID.
            step_number: The step number to update.
            **updates: Fields to update on the step.
        """
        session = self._sessions.get(task_id)
        if not session:
            raise ValueError(f"Session not found: {task_id}")

        for step in session.steps:
            if step.step_number == step_number:
                for key, value in updates.items():
                    if hasattr(step, key):
                        setattr(step, key, value)
                return

        raise ValueError(f"Step not found: {step_number}")

    def end_session(
        self,
        task_id: str,
        final_result: str,
        success: bool
    ) -> Path:
        """
        End a task session and generate reports.

        Args:
            task_id: The task session ID.
            final_result: Description of the final result.
            success: Whether the task completed successfully.

        Returns:
            Path to the generated report.
        """
        session = self._sessions.get(task_id)
        if not session:
            raise ValueError(f"Session not found: {task_id}")

        session.status = "completed" if success else "failed"
        session.completed_at = datetime.now().isoformat()

        # Save JSON data
        self._save_json(session, final_result)

        # Generate Markdown report
        report_path = self._generate_report(session, final_result)

        return report_path

    def list_tasks(self, limit: int = 20) -> list[dict]:
        """
        List recent tasks from the filesystem.

        Args:
            limit: Maximum number of tasks to return.

        Returns:
            List of task summaries.
        """
        tasks = []

        if not self.BASE_DIR.exists():
            return tasks

        # Get all task directories, sorted by name (which includes date)
        task_dirs = sorted(
            [d for d in self.BASE_DIR.iterdir() if d.is_dir() and d.name.startswith("task_")],
            reverse=True
        )[:limit]

        for task_dir in task_dirs:
            json_file = task_dir / "task.json"
            if json_file.exists():
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    tasks.append({
                        "task_id": data.get("task_id", task_dir.name),
                        "user_request": data.get("user_request", ""),
                        "status": data.get("status", "unknown"),
                        "created_at": data.get("created_at", ""),
                        "total_steps": data.get("summary", {}).get("total_steps", 0),
                    })
                except Exception:
                    tasks.append({
                        "task_id": task_dir.name,
                        "status": "unknown",
                    })

        return tasks

    def _generate_task_id(self) -> str:
        """Generate a unique task ID: task_YYYYMMDD_NNN."""
        date_str = datetime.now().strftime("%Y%m%d")
        existing = list(self.BASE_DIR.glob(f"task_{date_str}_*"))
        seq = len(existing) + 1
        return f"task_{date_str}_{seq:03d}"

    def _save_json(self, session: TaskSession, final_result: str) -> None:
        """Save complete task data as JSON."""
        success_steps = sum(1 for s in session.steps if s.result.get("success"))
        failed_steps = sum(1 for s in session.steps if not s.result.get("success", True))

        data = {
            "task_id": session.task_id,
            "created_at": session.created_at,
            "completed_at": session.completed_at,
            "status": session.status,
            "user_request": session.user_request,
            "device": session.device,
            "steps": [asdict(s) for s in session.steps],
            "summary": {
                "total_steps": len(session.steps),
                "success_steps": success_steps,
                "failed_steps": failed_steps,
                "final_result": final_result,
            },
        }

        json_path = session.task_dir / "task.json"
        json_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def _generate_report(self, session: TaskSession, final_result: str) -> Path:
        """Generate a Markdown report for the task."""
        status_emoji = "✅" if session.status == "completed" else "❌"
        status_text = "完成" if session.status == "completed" else "失败"

        lines = [
            f"# 任务报告: {session.task_id}\n",
            f"**用户请求**: {session.user_request}",
            f"**开始时间**: {session.created_at}",
            f"**结束时间**: {session.completed_at}",
            f"**状态**: {status_emoji} {status_text}\n",
            "---\n",
        ]

        for step in session.steps:
            result_emoji = "✅" if step.result.get("success") else "❌"

            lines.extend([
                f"## 步骤 {step.step_number}\n",
                f"**时间**: {step.timestamp}",
                f"**当前应用**: {step.current_app}\n",
            ])

            if step.claude_analysis:
                lines.extend([
                    "### Claude 分析",
                    f"{step.claude_analysis}\n",
                ])

            if step.claude_decision:
                lines.extend([
                    "### Claude 决策",
                    f"{step.claude_decision}\n",
                ])

            if step.action:
                lines.extend([
                    "### 执行操作",
                    f"- **类型**: {step.action.get('type', 'unknown')}",
                ])

                if step.action.get("element"):
                    lines.append(f"- **位置**: {step.action['element']}")
                if step.action.get("text"):
                    lines.append(f"- **文本**: {step.action['text']}")
                if step.action.get("description"):
                    lines.append(f"- **描述**: {step.action['description']}")

                lines.append("")

            if step.autoglm_response:
                thinking = step.autoglm_response.get("thinking", "")
                if thinking:
                    lines.extend([
                        "### AutoGLM 思考",
                        f"{thinking}\n",
                    ])

            # Add screenshots if available
            if step.screenshot_before or step.screenshot_after:
                lines.append("### 截图")
                lines.append("| 操作前 | 操作后 |")
                lines.append("|--------|--------|")

                before_img = f"![before]({step.screenshot_before})" if step.screenshot_before else "-"
                after_img = f"![after]({step.screenshot_after})" if step.screenshot_after else "-"
                lines.append(f"| {before_img} | {after_img} |\n")

            # Result
            result_msg = step.result.get("message", "")
            result_text = f"{result_emoji} {'成功' if step.result.get('success') else '失败'}"
            if result_msg:
                result_text += f": {result_msg}"

            lines.extend([
                "### 结果",
                f"{result_text}\n",
                "---\n",
            ])

        # Summary
        success_steps = sum(1 for s in session.steps if s.result.get("success"))
        failed_steps = len(session.steps) - success_steps

        lines.extend([
            "## 总结\n",
            f"- **总步数**: {len(session.steps)}",
            f"- **成功步数**: {success_steps}",
            f"- **失败步数**: {failed_steps}",
            f"- **最终结果**: {final_result}",
        ])

        report_path = session.task_dir / "report.md"
        report_path.write_text("\n".join(lines), encoding="utf-8")

        return report_path


# Global tracker instance
_tracker: TaskTracker | None = None


def get_tracker() -> TaskTracker:
    """Get the global TaskTracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = TaskTracker()
    return _tracker
