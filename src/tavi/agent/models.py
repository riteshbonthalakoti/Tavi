from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from tavi.core.models import Observation

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TaskRequest(BaseModel):
    task_name: str
    workspace_root: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    request_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaskContext(BaseModel):
    request: TaskRequest
    current_state: str = "START"
    observations: List[Observation] = Field(default_factory=list)
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    transition_count: int = 0
    max_transitions: int = 50
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaskResult(BaseModel):
    task_name: str
    request_id: str
    status: TaskStatus
    success: bool
    observations: List[Observation]
    structured_data: Dict[str, Any]
    error: Optional[str] = None
    duration: float = 0.0
    final_state: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
