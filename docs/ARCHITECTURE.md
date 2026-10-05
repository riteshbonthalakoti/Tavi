# Tavi Architecture

**Tavi is a local, deterministic personal agent that does not use an LLM at runtime.** It relies on deterministic state machines, exact rule matching, intent classification, and explicit tool execution under centralized security policies.

## Application Architecture

```text
User Message / Terminal Interface (tavi.cli)
    ↓
ApplicationService
    ↓
IntentEngine (Deterministic Classification)
    ├── Conversational Intent (greeting, status, farewell, help)
    │       ↓
    │   ConversationEngine
    │       ↓
    │   Deterministic Response Template
    │
    └── Task Intent (e.g., inspect_project)
            ↓
        AgentEngine (FSM / Side-effects)
            ↓
        Task State Machine Workflow
            ↓
        PermissionMiddleware (Centralized Security)
            ↓
        ToolRegistry
            ↓
        BaseTool (Execution)
            ↓
        Structured Observation & Result
```

## Core Components
- **CLI (`tavi.cli`)**: An interactive, minimal terminal interface using `rich` and `prompt_toolkit`. Features a compact information hierarchy, continuous conversation flow, and terminal-native tree visualizations. Normal mode provides a clean product UX, while `TAVI_DEBUG=1` exposes developer diagnostics.
- **ApplicationService**: Shared entry point unifying CLI and potential web interfaces. Classifies incoming messages and separates conversational interactions from task workflows.
- **ConversationEngine**: Purely deterministic responder for conversational intents (`greeting`, `status`, `farewell`, `help`). Bypasses the workflow execution pipeline and produces zero side effects.
- **IntentEngine**: Deterministically normalizes and maps natural language inputs into recognized task or conversation intents via compiled regular expressions. Does not use LLMs, embeddings, or fuzzy heuristics.
- **IntentRegistry**: Pattern-based registry registering task and conversation rules.
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

