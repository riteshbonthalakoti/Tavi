import time
from typing import Optional
from tavi.core.models import ToolRequest, ToolResult, PermissionDecision
from tavi.tools.registry import ToolRegistry
from tavi.security.policy import PermissionPolicy
from tavi.security.confirmation import ConfirmationProvider, DefaultConfirmationProvider

class PermissionMiddleware:
    """
    Intercepts tool requests, enforces the PermissionPolicy, 
    and handles confirmation prompting if required.
    """
    def __init__(self, 
                 registry: ToolRegistry, 
                 policy: PermissionPolicy, 
                 confirmation_provider: Optional[ConfirmationProvider] = None):
        self.registry = registry
        self.policy = policy
        self.confirmation_provider = confirmation_provider or DefaultConfirmationProvider()

    def execute_request(self, request: ToolRequest) -> ToolResult:
        start_time = time.time()
        
        try:
            tool = self.registry.get_tool(request.tool_name)
        except KeyError as e:
            return ToolResult(
                request_id=request.request_id,
                success=False,
                error=str(e),
                metadata={"duration_sec": time.time() - start_time}
            )

        decision = self.policy.evaluate(tool, request)

        if decision == PermissionDecision.BLOCK:
            return ToolResult(
                request_id=request.request_id,
                success=False,
                error=f"Execution blocked by permission policy: {request.tool_name}",
                metadata={"duration_sec": time.time() - start_time, "decision": decision}
            )

        if decision == PermissionDecision.CONFIRM:
            warning_message = f"Tool '{request.tool_name}' requires confirmation. Arguments: {request.arguments}"
            confirmed = self.confirmation_provider.request_confirmation(request, warning_message)
            if not confirmed:
                return ToolResult(
                    request_id=request.request_id,
                    success=False,
                    error=f"Execution denied by user: {request.tool_name}",
                    metadata={"duration_sec": time.time() - start_time, "decision": decision}
                )

        # Allow execution
        try:
            return tool.execute(request.request_id, request.arguments)
        except Exception as e:
            return ToolResult(
                request_id=request.request_id,
                success=False,
                error=f"Unhandled tool exception: {str(e)}",
                metadata={"duration_sec": time.time() - start_time}
            )
