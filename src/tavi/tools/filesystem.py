import os
import time
from pathlib import Path
from typing import Dict, Any
from tavi.core.models import ToolMetadata, PermissionLevel, ToolResult
from tavi.tools.base import BaseTool

class FileSystemTool(BaseTool):
    def __init__(self, workspace_root: str, max_bytes: int = 100 * 1024):
        self.workspace_root = Path(workspace_root).resolve()
        self.max_bytes = max_bytes
        self._metadata = ToolMetadata(
            name="filesystem",
            description="Perform read-only operations on the local file system within a workspace.",
            permission_level=PermissionLevel.SAFE,
            supported_operations=["list_directory", "read_file", "file_exists", "directory_exists"]
        )

    @property
    def metadata(self) -> ToolMetadata:
        return self._metadata

    def _resolve_and_verify_path(self, path: str) -> Path:
        """
        Resolves a path relative to workspace_root and ensures it does not escape.
        """
        try:
            # Resolve resolves symlinks and standardizes the path
            abs_path = (self.workspace_root / path).resolve()
            
            # Check if it strictly remains within the workspace root
            # is_relative_to is Python 3.9+
            if not abs_path.is_relative_to(self.workspace_root):
                raise ValueError(f"Path escapes workspace boundary: {path}")
                
            return abs_path
        except Exception as e:
            raise ValueError(f"Invalid path or escape attempted: {e}")

    def execute(self, request_id: str, arguments: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        operation = arguments.get("operation")
        path = arguments.get("path", ".")

        try:
            abs_path = self._resolve_and_verify_path(path)
            
            if operation == "list_directory":
                if not abs_path.is_dir():
                    raise ValueError(f"Path is not a directory: {path}")
                output = os.listdir(abs_path)
            elif operation == "read_file":
                if not abs_path.is_file():
                    raise ValueError(f"Path is not a file: {path}")
                    
                file_size = abs_path.stat().st_size
                if file_size > self.max_bytes:
                    raise ValueError(f"File size ({file_size} bytes) exceeds limit ({self.max_bytes} bytes).")
                    
                with open(abs_path, "r", encoding="utf-8") as f:
                    output = f.read(self.max_bytes + 1)
                    if len(output) > self.max_bytes:
                         raise ValueError(f"File content exceeds read limit of {self.max_bytes} bytes during read.")
            elif operation == "file_exists":
                output = abs_path.is_file()
            elif operation == "directory_exists":
                output = abs_path.is_dir()
            else:
                raise ValueError(f"Unsupported filesystem operation: {operation}")

            return ToolResult(
                request_id=request_id,
                success=True,
                output=output,
                metadata={"duration_sec": time.time() - start_time, "resolved_path": str(abs_path)}
            )
        except Exception as e:
            return ToolResult(
                request_id=request_id,
                success=False,
                error=str(e),
                metadata={"duration_sec": time.time() - start_time}
            )
