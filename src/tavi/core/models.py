from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Message(BaseModel):
    text: str
    sender: str  # 'user' or 'tavi'

class ConversationState(BaseModel):
    session_id: str
    history: List[Message] = []
    metadata: Dict[str, Any] = {}

class ResponseCandidate(BaseModel):
    text: str
    confidence: float
    source: str

from enum import Enum

class PermissionLevel(str, Enum):
    SAFE = "SAFE"
    CONFIRM = "CONFIRM"
    BLOCK = "BLOCK"

class PermissionDecision(str, Enum):
    ALLOW = "ALLOW"
    CONFIRM = "CONFIRM"
    BLOCK = "BLOCK"

class ToolMetadata(BaseModel):
    name: str
    description: str
    permission_level: PermissionLevel
    supported_operations: List[str] = []

class ToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    request_id: str
    source: str = "internal"

class ToolResult(BaseModel):
    success: bool
    output: Any = None
    error: Optional[str] = None
    exit_code: Optional[int] = None
    metadata: Dict[str, Any] = {}
    request_id: str

class Observation(BaseModel):
    kind: str
    message: str
    structured_data: Any = None
    source_tool: str
