from abc import ABC, abstractmethod
from tavi.core.models import ToolRequest

class ConfirmationProvider(ABC):
    """
    Abstract interface for requesting user confirmation.
    Allows CLI and Web to implement their own confirmation prompts.
    """
    @abstractmethod
    def request_confirmation(self, request: ToolRequest, warning_message: str) -> bool:
        """
        Returns True if the user confirmed, False otherwise.
        """
        pass

class DefaultConfirmationProvider(ConfirmationProvider):
    """
    A basic fallback provider that always denies.
    """
    def request_confirmation(self, request: ToolRequest, warning_message: str) -> bool:
        return False
