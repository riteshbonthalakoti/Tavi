from tavi.core.models import ConversationState, Message, ResponseCandidate
import logging

logger = logging.getLogger(__name__)

class ConversationEngine:
    """
    Main orchestrator for Tavi's conversational logic.
    """
    def __init__(self):
        logger.info("Initializing Conversation Engine")

    def process_message(self, text: str, session_id: str) -> str:
        """
        Processes a user message and returns Tavi's response.
        Milestone 1: Basic state tracking and echo response.
        """
        logger.debug(f"Processing message from session {session_id}: {text}")
        
        # Track user message
        user_message = Message(text=text, sender='user')
        state = ConversationState(session_id=session_id)
        state.history.append(user_message)
        
        # Generate response candidate
        candidate = ResponseCandidate(
            text=f"Tavi heard: {text}",
            confidence=1.0,
            source="echo_module"
        )
        
        # Track Tavi's response
        tavi_message = Message(text=candidate.text, sender='tavi')
        state.history.append(tavi_message)
        
        logger.info(f"Generated response with confidence {candidate.confidence} from {candidate.source}")
        
        return candidate.text
