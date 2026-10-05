import subprocess
import time
import os
from typing import Dict, Any, Optional
from tavi.core.models import ToolMetadata, PermissionLevel, ToolResult
from tavi.tools.base import BaseTool

class ShellTool(BaseTool):
    def __init__(self, timeout_sec: int = 10, default_cwd: Optional[str] = None):
        self.timeout_sec = timeout_sec
        self.default_cwd = default_cwd or os.getcwd()
        self._metadata = ToolMetadata(
            name="shell",
            description="Execute conservative shell commands safely. Must be a list of strings.",
            permission_level=PermissionLevel.CONFIRM,
            supported_operations=["execute_command"]
        )

    @property
    def metadata(self) -> ToolMetadata:
        return self._metadata
        
    def _get_safe_env(self) -> Dict[str, str]:
        """
        Creates a constrained environment variable dict for subprocess execution.
        Prevents leaking API keys and unnecessary sensitive tokens.
        """
        allowed_keys = {"PATH", "SystemRoot", "USERPROFILE", "TEMP", "TMP", "HOMEPATH", "HOMEDRIVE"}
        return {k: v for k, v in os.environ.items() if k in allowed_keys}

    def execute(self, request_id: str, arguments: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        command = arguments.get("command")
        cwd = arguments.get("cwd", self.default_cwd)
        
        if not isinstance(command, list):
            return ToolResult(
                request_id=request_id,
                success=False,
                error="Command must be provided as a list of strings to prevent shell injection.",
                metadata={"duration_sec": time.time() - start_time}
            )
            
        try:
            # We strictly enforce shell=False for safety and predictable execution.
            result = subprocess.run(
                command,
                cwd=cwd,
                env=self._get_safe_env(),
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                shell=False
            )
            return ToolResult(
                request_id=request_id,
                success=result.returncode == 0,
                output={"stdout": result.stdout, "stderr": result.stderr},
                exit_code=result.returncode,
                metadata={"duration_sec": time.time() - start_time, "command": command, "cwd": cwd}
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                request_id=request_id,
                success=False,
                error=f"Command timed out after {self.timeout_sec} seconds.",
                metadata={"duration_sec": time.time() - start_time, "command": command}
            )
        except Exception as e:
            return ToolResult(
                request_id=request_id,
                success=False,
                error=str(e),
                metadata={"duration_sec": time.time() - start_time, "command": command}
            )
