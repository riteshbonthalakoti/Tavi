# Tavi Architecture

**Tavi does not use an LLM at runtime.** It relies on deterministic state machines, classical NLP, intent classification, and explicit tool execution.

## Application Architecture

```text
Interface (Web/CLI)
    ↓
ApplicationService
    ↓
ConversationEngine (NLP / Dialogue)
    ↓
AgentEngine (FSM / Side-effects)
    ↓
Task State Machine
    ↓
PermissionMiddleware (Centralized Security)
    ↓
ToolRegistry
    ↓
BaseTool (Execution)
    ↓
Structured Observation
```

## Core Components
- **ApplicationService**: Shared entry point unifying Web and CLI usage. Orchestrates incoming user requests.
- **IntentEngine**: Deterministically normalizes and maps natural language inputs into recognized task intents. Does not use LLMs.
- **IntentRegistry**: Strict pattern-based registry matching user phrases to workflows.
- **AgentEngine**: Executes deterministic FSM workflows safely through the permission layer.
- **WorkflowRegistry**: Stores and resolves predefined Agent workflows.
- **ToolRegistry**: Resolves tools by name deterministically.
- **BaseTool**: Strict contract enforcing `execute()` returning `ToolResult`.
- **TaskRequest/TaskResult**: Standardized models for cross-component workflow communication.
- **PermissionPolicy**: Centralized rules engine mapping tools/operations to `SAFE`, `CONFIRM`, or `BLOCK`.
- **ConfirmationProvider**: Abstract interface allowing CLI or Web to handle `CONFIRM` decisions.

## Tool Boundaries
- **Filesystem**: Enforces an application-level workspace boundary (`workspace_root`). Rejects directory traversal (`..`) and absolute path escapes. `max_bytes` protects against unbounded memory consumption during reads. Writes are blocked.
- **Shell**: `shell=True` is explicitly rejected. Accepts structured command arguments (`list[str]`). The execution environment (`cwd`, `env`) is strictly controlled to prevent accidental credential leakage. Infinite execution is prevented via hard timeouts.
- **Git**: `git` tool provides read-only repository inspection (`status`, `diff`, `log`).

