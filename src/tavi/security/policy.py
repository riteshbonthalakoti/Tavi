from typing import Dict, List
from tavi.core.models import ToolRequest, PermissionDecision, PermissionLevel
from tavi.tools.base import BaseTool

class PermissionPolicy:
    """
    Centralized rules engine for determining if a tool execution is allowed.
    """
    def evaluate(self, tool: BaseTool, request: ToolRequest) -> PermissionDecision:
        # Currently defaults to the tool's defined permission level.
        # Future enhancement: Operation-specific or argument-specific policies.
        level = tool.metadata.permission_level
        
        if level == PermissionLevel.SAFE:
            return PermissionDecision.ALLOW
        elif level == PermissionLevel.CONFIRM:
            return PermissionDecision.CONFIRM
        else:
            return PermissionDecision.BLOCK
