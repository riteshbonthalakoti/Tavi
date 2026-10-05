import pytest
import os
from tavi.core.models import ToolRequest, PermissionLevel
from tavi.tools.registry import ToolRegistry
from tavi.tools.filesystem import FileSystemTool
from tavi.tools.shell import ShellTool
from tavi.tools.git import GitTool

def test_registry_operations():
    registry = ToolRegistry()
    fs_tool = FileSystemTool(workspace_root=".")
    
    registry.register(fs_tool)
    assert "filesystem" in registry.list_tools()
    
    with pytest.raises(ValueError):
        registry.register(fs_tool)
        
    assert registry.get_tool("filesystem") == fs_tool
    
    with pytest.raises(KeyError):
        registry.get_tool("missing_tool")
        
    registry.unregister("filesystem")
    assert "filesystem" not in registry.list_tools()

def test_filesystem_tool(tmp_path):
    tool = FileSystemTool(workspace_root=str(tmp_path), max_bytes=100)
    assert tool.metadata.permission_level == PermissionLevel.SAFE
    
    # Existing file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello World")
    
    req_id = "test-1"
    res = tool.execute(req_id, {"operation": "file_exists", "path": "test.txt"})
    assert res.success is True
    assert res.output is True
    
    # Missing file
    res = tool.execute(req_id, {"operation": "file_exists", "path": "does_not_exist.txt"})
    assert res.success is True
    assert res.output is False
    
    # Read file
    res = tool.execute(req_id, {"operation": "read_file", "path": "test.txt"})
    assert res.success is True
    assert res.output == "Hello World"
    
    # Invalid operation
    res = tool.execute(req_id, {"operation": "write_file", "path": "test.txt"})
    assert res.success is False
    assert "Unsupported filesystem operation" in res.error

def test_filesystem_sandbox(tmp_path):
    tool = FileSystemTool(workspace_root=str(tmp_path), max_bytes=100)
    req_id = "test-sandbox"
    
    # A. Filesystem traversal
    res = tool.execute(req_id, {"operation": "file_exists", "path": "../../outside.txt"})
    assert res.success is False
    assert "escapes workspace boundary" in res.error
    
    # B. Absolute path outside workspace
    outside_path = tmp_path.parent / "secret.txt"
    res = tool.execute(req_id, {"operation": "file_exists", "path": str(outside_path)})
    assert res.success is False
    assert "escapes workspace boundary" in res.error

    # C. Symlink escape (if platform supports it)
    try:
        symlink_path = tmp_path / "link"
        symlink_path.symlink_to(tmp_path.parent)
        res = tool.execute(req_id, {"operation": "list_directory", "path": "link"})
        assert res.success is False
        assert "escapes workspace boundary" in res.error
    except OSError:
        pass

    # F. Huge file protection
    huge_file = tmp_path / "huge.txt"
    huge_file.write_text("A" * 200) # Exceeds max_bytes of 100
    res = tool.execute(req_id, {"operation": "read_file", "path": "huge.txt"})
    assert res.success is False
    assert "exceeds limit" in res.error

def test_shell_tool():
    tool = ShellTool(timeout_sec=2)
    assert tool.metadata.permission_level == PermissionLevel.CONFIRM
    
    # Valid command
    req_id = "test-2"
    res = tool.execute(req_id, {"command": ["python", "--version"]})
    assert res.success is True
    assert "Python" in res.output["stdout"]
    assert res.exit_code == 0
    
    # Invalid command format (string instead of list)
    res = tool.execute(req_id, {"command": "python --version"})
    assert res.success is False
    assert "must be provided as a list" in res.error
    
    # Failing command
    res = tool.execute(req_id, {"command": ["python", "-c", "import sys; sys.exit(1)"]})
    assert res.success is False
    assert res.exit_code == 1
    
    # E. Shell timeout
    res = tool.execute(req_id, {"command": ["python", "-c", "import time; time.sleep(5)"]})
    assert res.success is False
    assert "timed out" in res.error

def test_git_tool():
    tool = GitTool()
    assert tool.metadata.permission_level == PermissionLevel.SAFE
    
    # Git status (assuming tests run in a repo)
    req_id = "test-3"
    res = tool.execute(req_id, {"operation": "status"})
    assert res.success is True
    assert "On branch" in res.output or "HEAD" in res.output
    
    # Invalid operation
    res = tool.execute(req_id, {"operation": "commit"})
    assert res.success is False
    assert "Unsupported git operation" in res.error
