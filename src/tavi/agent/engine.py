import time
from tavi.agent.models import TaskRequest, TaskContext, TaskResult, TaskStatus
from tavi.agent.registry import WorkflowRegistry
from tavi.security.permissions import PermissionMiddleware

class AgentEngine:
    def __init__(self, workflow_registry: WorkflowRegistry, permission_middleware: PermissionMiddleware):
        self.workflow_registry = workflow_registry
        self.permission_middleware = permission_middleware

    def execute_task(self, request: TaskRequest) -> TaskResult:
        start_time = time.time()
        
        try:
            workflow = self.workflow_registry.get_workflow(request.task_name)
        except Exception as e:
            return TaskResult(
                task_name=request.task_name,
                request_id=request.request_id,
                status=TaskStatus.FAILED,
                success=False,
                observations=[],
                structured_data={},
                error=f"Failed to resolve workflow: {str(e)}",
                duration=time.time() - start_time,
                final_state="START"
            )

        context = TaskContext(request=request)
        
        while not workflow.is_terminal(context.current_state):
            if context.transition_count >= context.max_transitions:
                return self._fail_result(context, start_time, "Maximum workflow transitions exceeded.")
                
            try:
                next_state = workflow.execute_state(context.current_state, context, self.permission_middleware)
                context.current_state = next_state
                context.transition_count += 1
            except Exception as e:
                return self._fail_result(context, start_time, f"State execution failed at {context.current_state}: {str(e)}")
                
        is_success = (context.current_state == "SUCCESS")
        
        return TaskResult(
            task_name=request.task_name,
            request_id=request.request_id,
            status=TaskStatus.COMPLETED if is_success else TaskStatus.FAILED,
            success=is_success,
            observations=context.observations,
            structured_data=context.structured_data,
            error=None if is_success else context.structured_data.get("error_reason", "Workflow terminated in FAILURE state without explicit error."),
            duration=time.time() - start_time,
            final_state=context.current_state,
            metadata=context.metadata
        )

    def _fail_result(self, context: TaskContext, start_time: float, error_msg: str) -> TaskResult:
        return TaskResult(
            task_name=context.request.task_name,
            request_id=context.request.request_id,
            status=TaskStatus.FAILED,
            success=False,
            observations=context.observations,
            structured_data=context.structured_data,
            error=error_msg,
            duration=time.time() - start_time,
            final_state=context.current_state,
            metadata=context.metadata
        )
