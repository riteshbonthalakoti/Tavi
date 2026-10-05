import pytest
from typing import Dict, Any
from tavi.core.models import ToolRequest, ToolResult, PermissionLevel, ToolMetadata
from tavi.tools.base import BaseTool
from tavi.tools.registry import ToolRegistry
from tavi.security.policy import PermissionPolicy
from tavi.security.permissions import PermissionMiddleware
from tavi.security.confirmation import ConfirmationProvider

class DummyTool(BaseTool):
    def __init__(self, name: str, level: PermissionLevel):
        self._metadata = ToolMetadata(
            name=name,
            description="Dummy tool for testing",
            permission_level=level
        )
    
    @property
    def metadata(self) -> ToolMetadata:
        return self._metadata
        
    def execute(self, request_id: str, arguments: Dict[str, Any]) -> ToolResult:
        return ToolResult(request_id=request_id, success=True, output="dummy_success")

class MockConfirmationProvider(ConfirmationProvider):
    def __init__(self, will_confirm: bool):
        self.will_confirm = will_confirm
        
    def request_confirmation(self, request: ToolRequest, warning_message: str) -> bool:
        return self.will_confirm

def test_permission_middleware():
    registry = ToolRegistry()
    registry.register(DummyTool("safe_tool", PermissionLevel.SAFE))
    registry.register(DummyTool("confirm_tool", PermissionLevel.CONFIRM))
    registry.register(DummyTool("block_tool", PermissionLevel.BLOCK))
    
    policy = PermissionPolicy()
    
    # Test SAFE
    middleware = PermissionMiddleware(registry, policy)
    req = ToolRequest(tool_name="safe_tool", arguments={}, request_id="1")
    res = middleware.execute_request(req)
    assert res.success is True
    assert res.output == "dummy_success"
    
    # Test BLOCK
    req = ToolRequest(tool_name="block_tool", arguments={}, request_id="2")
    res = middleware.execute_request(req)
    assert res.success is False
    assert "Execution blocked" in res.error
    
    # Test CONFIRM (Denied)
    middleware_deny = PermissionMiddleware(registry, policy, MockConfirmationProvider(False))
    req = ToolRequest(tool_name="confirm_tool", arguments={}, request_id="3")
    res = middleware_deny.execute_request(req)
    assert res.success is False
    assert "Execution denied by user" in res.error
    
    # Test CONFIRM (Approved)
    middleware_approve = PermissionMiddleware(registry, policy, MockConfirmationProvider(True))
    res = middleware_approve.execute_request(req)
    assert res.success is True
    assert res.output == "dummy_success"
    
    # Test Missing Confirmation Provider (Fail-Closed)
    middleware_default = PermissionMiddleware(registry, policy)
    res = middleware_default.execute_request(req)
    assert res.success is False
    assert "Execution denied by user" in res.error
    req = ToolRequest(tool_name="missing_tool", arguments={}, request_id="4")
    res = middleware.execute_request(req)
    assert res.success is False
    assert "missing_tool" in res.error
