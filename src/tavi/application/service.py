import logging
from tavi.conversation.engine import ConversationEngine

logger = logging.getLogger(__name__)

class ApplicationService:
    """
    Unified entry point for Web and CLI interfaces.
    """
    def __init__(self):
        logger.info("Initializing Application Service")
        self.conversation_engine = ConversationEngine()
        # TODO: Initialize AgentEngine, Memory, ToolRegistry, PermissionMiddleware

    def process_chat(self, text: str, session_id: str) -> str:
        """
        Handles incoming chat messages and routes them through the Tavi engine.
        """
        return self.conversation_engine.process_message(text, session_id)
