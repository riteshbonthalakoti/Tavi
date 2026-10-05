from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, Optional
from tavi.agent.models import TaskContext
from tavi.security.permissions import PermissionMiddleware
from tavi.core.models import ToolRequest

# A StateHandler is a function that takes the current context and the PermissionMiddleware
# It returns the name of the next state (str).
StateHandler = Callable[[TaskContext, PermissionMiddleware], str]

class BaseWorkflow(ABC):
    """
    Abstract deterministic FSM Workflow.
    """
    def __init__(self):
        self._states: Dict[str, StateHandler] = {}
        self._terminal_states = {"SUCCESS", "FAILURE"}
        self.register_states()
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the workflow, used to resolve from registry."""
        pass

    @abstractmethod
    def register_states(self) -> None:
        """Register states to self._states here."""
        pass

    def add_state(self, name: str, handler: StateHandler) -> None:
        self._states[name] = handler

    def execute_state(self, state_name: str, context: TaskContext, middleware: PermissionMiddleware) -> str:
        """
        Executes a single state and returns the next state transition.
        """
        if state_name in self._terminal_states:
            return state_name
            
        handler = self._states.get(state_name)
        if not handler:
            raise ValueError(f"Unknown state '{state_name}' in workflow '{self.name}'")
            
        return handler(context, middleware)

    def is_terminal(self, state_name: str) -> bool:
        return state_name in self._terminal_states
