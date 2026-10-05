import logging
import uuid
import os
from pydantic import BaseModel
from typing import Optional
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
from tavi.agent.intent import IntentRegistry, IntentEngine

logger = logging.getLogger(__name__)

class MessageResult(BaseModel):
    intent_name: Optional[str] = None
    confidence: float
    executed: bool
    response_text: str
    task_result: Optional[TaskResult] = None

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

        # Intent Engine setup
        self.intent_registry = IntentRegistry()

        # Task intents
        self.intent_registry.register("inspect_project", [
            r"^(can you\s+)?(please\s+)?inspect (this\s+)?project$",
            r"^(can you\s+)?(please\s+)?analyze (this\s+)?project$",
            r"^(can you\s+)?(please\s+)?analyze (this\s+)?repository$",
            r"^(can you\s+)?(please\s+)?check (this\s+)?project$",
            r"^(can you\s+)?(please\s+)?check (this\s+)?repository$",
            r"^(can you\s+)?(please\s+)?show project structure$"
        ], intent_type="task")

        # Conversational intents
        self.intent_registry.register("greeting", [
            r"^(hi|hello|hey|hey there|hello there)(\s+tavi)?$",
            r"^good\s+(morning|afternoon|evening)(\s+tavi)?$",
        ], intent_type="conversation")

        self.intent_registry.register("status", [
            r"^how\s+are\s+you(\s+doing)?(\s+tavi)?$",
            r"^(are\s+)?you\s+okay(\s+tavi)?$",
            r"^how('?s|\s+is)\s+it\s+going(\s+tavi)?$",
            r"^how\s+are\s+things(\s+tavi)?$",
        ], intent_type="conversation")

        self.intent_registry.register("farewell", [
            r"^(bye|goodbye|cya)(\s+tavi)?$",
            r"^see\s+(you|ya)(\s+later)?(\s+tavi)?$",
            r"^good\s*night(\s+tavi)?$",
        ], intent_type="conversation")

        self.intent_registry.register("help", [
            r"^help$",
            r"^what\s+can\s+you\s+do$",
            r"^how\s+do\s+i\s+use\s+this$",
            r"^commands$",
        ], intent_type="conversation")

        self.intent_engine = IntentEngine(self.intent_registry)

    def process_chat(self, text: str, session_id: str) -> str:
        """
        Legacy endpoint processing basic message echo.
        """
        return self.conversation_engine.process_message(text, session_id)

    def handle_message(self, message: str) -> MessageResult:
        """
        Classifies incoming natural language, routing conversational intents to
        the ConversationEngine and task intents to the AgentEngine.
        """
        intent_result = self.intent_engine.classify(message)

        if not intent_result.is_supported or not intent_result.intent_name:
            return MessageResult(
                intent_name=None,
                confidence=0.0,
                executed=False,
                response_text="I don't have a workflow for that yet. Try asking me to inspect your project.",
                task_result=None
            )

        # Conversational intent: purely deterministic responses without workflow execution
        if intent_result.intent_type == "conversation":
            response_text = self.conversation_engine.get_response(intent_result.intent_name)
            return MessageResult(
                intent_name=intent_result.intent_name,
                confidence=intent_result.confidence,
                executed=False,
                response_text=response_text,
                task_result=None
            )

        # Task intent: executed via AgentEngine -> Workflow -> PermissionMiddleware -> Tools
        task_result = self.run_task(intent_result.intent_name, intent_result.arguments)

        if task_result.success:
            response_text = f"Task {intent_result.intent_name} completed successfully."
        else:
            response_text = f"Task {intent_result.intent_name} failed: {task_result.error}"

        return MessageResult(
            intent_name=intent_result.intent_name,
            confidence=intent_result.confidence,
            executed=True,
            response_text=response_text,
            task_result=task_result
        )

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
