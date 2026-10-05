# Tavi

Tavi is a local, non-LLM conversational and agentic companion.

## What is Tavi?

Tavi is an original fictional-character and personal-companion chatbot designed for the **Hack Club Crescent Chatterbox** challenge. The project deliberately does NOT use an LLM at runtime.

## Non-LLM Design

**Tavi does not use an LLM at runtime.**

The planned intelligence is based on:
- deterministic rules
- finite-state workflows
- classical NLP
- TF-IDF retrieval
- Markov chains
- optional tiny self-trained intent classifier

## Current Architecture

The current architecture establishes a secure foundation for Tavi's execution environment:

- **ConversationEngine**
- **ApplicationService**
- **ToolRegistry**
- **PermissionMiddleware**
- **FilesystemTool**
- **ShellTool**
- **GitTool**
- **AgentEngine** (Planned)
- deterministic FSM workflows (Planned)
- future classical NLP components (Planned)

## Security

Security is critical to Tavi's architecture since it runs on your local machine:
- workspace-bounded filesystem access
- bounded file reads
- `shell=False` strict execution
- structured shell commands
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
| AgentEngine | Planned / In progress |
| FSM workflows | Planned / In progress |
| Conversational NLP | Planned |
| Web UI | In progress / Planned |

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
