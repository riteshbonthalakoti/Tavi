import logging
import uuid
import os
from tavi.conversation.engine import ConversationEngine
from tavi.agent.engine import AgentEngine
from tavi.agent.registry import WorkflowRegistry
from tavi.agent.workflows.inspect_project import InspectProjectWorkflow
from tavi.tools.registry import ToolRegistry
from tavi.tools.filesystem import FileSystemTool
from tavi.tools.shell import ShellTool
from tavi.tools.git import GitTool
from tavi.security.permissions import PermissionMiddleware
from tavi.security.policy import PermissionPolicy
from tavi.agent.models import TaskRequest, TaskResult

logger = logging.getLogger(__name__)

class ApplicationService:
    """
    Unified entry point for Web and CLI interfaces.
    """
    def __init__(self, workspace_root: str = "."):
        logger.info("Initializing Application Service")
        self.workspace_root = workspace_root
        self.conversation_engine = ConversationEngine()

        # Tools & Security setup
        self.tool_registry = ToolRegistry()
        self.tool_registry.register(FileSystemTool(workspace_root=self.workspace_root))
        self.tool_registry.register(ShellTool(default_cwd=self.workspace_root))
        self.tool_registry.register(GitTool(workspace_root=self.workspace_root))


        self.permission_policy = PermissionPolicy()
        self.permission_middleware = PermissionMiddleware(self.tool_registry, self.permission_policy)

        # Agent Engine setup
        self.workflow_registry = WorkflowRegistry()
        self.workflow_registry.register(InspectProjectWorkflow())
        self.agent_engine = AgentEngine(self.workflow_registry, self.permission_middleware)

    def process_chat(self, text: str, session_id: str) -> str:
        """
        Handles incoming chat messages and routes them through the Tavi engine.
        """
        return self.conversation_engine.process_message(text, session_id)

    def run_task(self, task_name: str, arguments: dict = None) -> TaskResult:
        """
        Directly executes a deterministic workflow using the AgentEngine.
        """
        req = TaskRequest(
            task_name=task_name,
            workspace_root=self.workspace_root,
            arguments=arguments or {},
            request_id=str(uuid.uuid4())
        )
        return self.agent_engine.execute_task(req)
