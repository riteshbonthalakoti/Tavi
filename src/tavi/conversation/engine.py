from tavi.core.models import ConversationState, Message, ResponseCandidate
import logging

logger = logging.getLogger(__name__)

class ConversationEngine:
    """
    Deterministic conversation engine for conversational intents.
    """
    RESPONSES = {
        "greeting": "Hey. I'm Tavi.\nWhat are we working on?",
        "status": "Running smoothly. What should we work on?",
        "farewell": "See you.\nI'll be here when you need me.",
        "help": "I can inspect and analyze your workspace repository.\nTry: 'inspect this project'",
    }

    def __init__(self):
        logger.info("Initializing Conversation Engine")

    def get_response(self, intent_name: str) -> str:
        """
        Returns a deterministic response for a recognized conversational intent.
        """
        return self.RESPONSES.get(
            intent_name,
            "I don't have a workflow for that yet. Try asking me to inspect your project."
        )

    def process_message(self, text: str, session_id: str) -> str:
        """
        Processes a user message and returns Tavi's response.
        Milestone 1 legacy endpoint: basic state tracking and echo response.
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
