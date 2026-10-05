from abc import ABC, abstractmethod
from typing import Dict, Any
from tavi.core.models import ToolMetadata, ToolResult

class BaseTool(ABC):
    """
    Strict contract for all tools executable by the AgentEngine.
    """
    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        pass

    @abstractmethod
    def execute(self, request_id: str, arguments: Dict[str, Any]) -> ToolResult:
        """
        Executes the tool with the given arguments and returns a structured ToolResult.
        """
        pass
