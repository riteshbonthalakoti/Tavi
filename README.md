# Tavi

Tavi is a local, deterministic personal agent and conversational companion.

## What is Tavi?

Tavi is an original character and local agent designed for the **Hack Club Crescent Chatterbox** challenge. The project deliberately does NOT use an LLM, external AI API, or network runtime.

## Non-LLM Design

**Tavi does not use an LLM at runtime.**

The intelligence is built on:
- deterministic regex and rule matching
- finite-state machine (FSM) workflows
- deterministic conversation templates
- bounded, secure local tool execution

## Current Architecture

The architecture establishes a deterministic, secure execution environment:

- **CLI (`tavi.cli`)**: Minimal, compact terminal interface powered by `rich` and `prompt_toolkit`.
- **ApplicationService**: Central coordinator separating conversational intents from task execution.
- **ConversationEngine**: Deterministic responses for conversational intents (`greeting`, `status`, `farewell`, `help`).
- **IntentEngine**: Rule-based intent classifier with normalization.
- **AgentEngine**: FSM executor managing task workflows.
- **WorkflowRegistry**: Deterministic state machine workflows (e.g., `inspect_project`).
- **PermissionMiddleware**: Security gateway enforcing safe operations.
- **ToolRegistry**: Secure tools (`FileSystemTool`, `ShellTool`, `GitTool`).

## Security

Security is critical to Tavi's architecture since it runs on your local machine:
- workspace-bounded filesystem access
- bounded file reads
- `shell=False` strict execution
- structured command arguments
- controlled subprocess environment
- timeout enforcement
- centralized permissions
- fail-closed confirmation
- read-only Git operations currently

## Current Status

| Component | Status |
|---|---|
| Core architecture | Complete |
| Tool system | Complete |
| Permission system | Complete |
| Filesystem security | Complete |
| Shell security | Complete |
| Git read-only tooling | Complete |
| AgentEngine | Complete |
| FSM workflows | Complete (inspect_project) |
| IntentEngine | Complete (deterministic intent classifier) |
| Conversation layer | Complete (deterministic greetings, status, farewell, help) |
| Interactive Terminal CLI | Complete (compact, continuous conversation) |
| Web UI | Planned |

## Development

To set up Tavi locally:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

To run tests:
```powershell
$env:PYTHONPATH="src"
pytest
```

## Project Structure

```
c:\Projects\Software Projects\Tavi
├── docs/                 # Architecture specifications
├── src/
│   ├── main_web.py       # Web entry point
│   └── tavi/             # Tavi core package
│       ├── application/  # Application service bridging CLI/Web
│       ├── conversation/ # NLP and dialogue engine
│       ├── core/         # Config and Pydantic models
│       ├── security/     # Centralized permission middleware
│       ├── tools/        # Tool registry and implementations
│       └── web/          # FastAPI web interface
├── static/               # HTML/CSS/JS frontend
├── tests/                # Pytest suites
└── requirements.txt      # Project dependencies
```

## Crescent

This project is being built for the **Hack Club Crescent Chatterbox card**. The implementation strictly adheres to the non-LLM constraints of the challenge.
