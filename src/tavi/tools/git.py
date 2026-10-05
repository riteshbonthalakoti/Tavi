import subprocess
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional
from tavi.core.models import ToolMetadata, PermissionLevel, ToolResult
from tavi.tools.base import BaseTool

class GitTool(BaseTool):
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or os.getcwd()
        self._metadata = ToolMetadata(
            name="git",
            description="Inspect git repository state.",
            permission_level=PermissionLevel.SAFE,
            supported_operations=["status", "diff", "log", "current_branch"]
        )

    @property
    def metadata(self) -> ToolMetadata:
        return self._metadata

    def _run_git(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git"] + args,
            cwd=self.workspace_root,
            capture_output=True,
            text=True,
            shell=False
        )

    def execute(self, request_id: str, arguments: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        operation = arguments.get("operation")

        try:
            # Verify git repo exists
            check_repo = self._run_git(["rev-parse", "--is-inside-work-tree"])
            if check_repo.returncode != 0:
                raise ValueError("Not a git repository.")

            if operation == "status":
                result = self._run_git(["status"])
            elif operation == "diff":
                result = self._run_git(["diff"])
            elif operation == "log":
                result = self._run_git(["log", "-n", "5"])
            elif operation == "current_branch":
                result = self._run_git(["branch", "--show-current"])
            else:
                raise ValueError(f"Unsupported git operation: {operation}")

            return ToolResult(
                request_id=request_id,
                success=result.returncode == 0,
                output=result.stdout.strip() if result.returncode == 0 else result.stderr.strip(),
                exit_code=result.returncode,
                metadata={"duration_sec": time.time() - start_time, "operation": operation}
            )
        except Exception as e:
            return ToolResult(
                request_id=request_id,
                success=False,
                error=str(e),
                metadata={"duration_sec": time.time() - start_time}
            )
