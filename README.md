# Tavi — Personal Terminal Workspace Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library%20Only-2ea44f?style=flat)
![Architecture](https://img.shields.io/badge/AI%20Models-Zero%20%2F%20Deterministic-blueviolet?style=flat)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat)
![Chatterbox](https://img.shields.io/badge/Hack%20Club-Chatterbox-ec3750?style=flat)

**A lightweight, deterministic personal workspace agent and web companion built from scratch without AI models or external dependencies.**

[🌐 Explore Live Web Demo](https://riteshbonthalakoti.github.io/Tavi/) · [📖 Command Reference](#command-reference) · [🚀 Getting Started](#getting-started)

</div>

---

## Overview

**Tavi** is a local-first personal developer assistant designed to run directly in your terminal and alongside your browser. Unlike modern assistants that rely on heavy language model APIs or remote inference servers, Tavi operates entirely **deterministically** using pattern-matched intent classification and standard library system introspection.

It runs instantly, requires zero `pip install` commands or virtual environments, and functions completely offline with full privacy.

---

## Visual Showcase

### Interactive Terminal Interface
The CLI launches with an interactive status card, showing your current workspace, active Git branch, dirty/clean status, and available commands:

![Tavi Terminal Agent](screenshot-cli.png)

### Web Companion Interface
A web companion replicating the terminal experience with interactive chips, live connection status, and instant responses:

![Tavi Web Interface](screenshot-web.png)

---

## Key Features

- **⚡ Zero External Dependencies**: Written exclusively using Python's standard library (`http.server`, `urllib`, `re`, `subprocess`, `pathlib`). No virtual environment or third-party packages required.
- **🔍 Deep Workspace Inspection**: Automatically detects project stacks (Python, Node.js, Rust, Go, Java), test runners (pytest), active Git branches, and working tree modification status.
- **💬 Natural Deterministic Conversation**: Understands conversational intents (greetings, status checks, capability queries, help, project analysis) without unpredictable model hallucinations.
- **💻 Dual Interface**:
  - **Terminal Agent CLI (`tavi.py`)**: Designed with rich ANSI styling, formatted dialogue blocks, UTF-8 safety across Windows/Linux/macOS, and session controls (`clear`, `exit`).
  - **Web Companion (`web.py` + `index.html`)**: Single-page dark mode interface with built-in client-side fallback, making it fully operational both locally and on static hosts like GitHub Pages.
- **🛡️ 100% Offline & Private**: Zero telemetry, zero cloud calls, zero credentials needed. All workspace inspections are strictly read-only and local to your machine.

---

## Getting Started

### Prerequisites

- **Python 3.10** or higher.
- **Git** (optional, for repository inspection features).

No extra package managers or virtual environments are needed.

### 1. Terminal Agent

Clone the repository and run the terminal agent:

```bash
git clone https://github.com/riteshbonthalakoti/Tavi.git
cd Tavi
python tavi.py
```

Type naturally into the prompt to interact with Tavi:

```text
› hello
› what can you do for me?
› inspect this project
› clear
› exit
```

### 2. Local Web Companion

Launch the local web server:

```bash
python web.py
```

Once running, navigate to `http://localhost:8000` in your browser. The server exposes:
- `GET /` — Serves the responsive web companion (`index.html`).
- `POST /chat` — JSON endpoint processing agent queries and returning structured replies.

Alternatively, try the hosted version directly at [riteshbonthalakoti.github.io/Tavi](https://riteshbonthalakoti.github.io/Tavi/).

---

## Command Reference

| Intent / Category | Sample Inputs | Tavi Response / Behavior |
| :--- | :--- | :--- |
| **Greeting** | `hi`, `hello`, `hey tavi`, `good morning` | Welcoming agent greeting ready for tasks. |
| **Status** | `how are you?`, `how's it going?`, `status` | System health and operational readiness status. |
| **Capabilities** | `what can you do?`, `features`, `capabilities` | Summary of workspace inspection and conversational capabilities. |
| **Workspace Inspection** | `inspect this project`, `check repository`, `analyze project` | Inspects current directory, Git branch, dirty tree, project stack, and test setup. |
| **Help & Guide** | `help`, `commands`, `how do i use this` | Interactive command guide and syntax tips. |
| **Session Control** | `clear`, `cls` | Clears terminal screen and re-renders the initiation card. |
| **Termination** | `exit`, `quit`, `q`, `bye` | Gracefully closes the session. |

---

## Architecture & Codebase

The repository is intentionally minimal, readable, and maintained by hand:

```text
Tavi/
├── tavi.py             # Core engine: intent classification, workspace inspector & terminal CLI
├── web.py              # Native Python HTTP server with CORS and JSON chat endpoint
├── index.html          # Modern dark-mode web companion with client-side fallback
├── screenshot-cli.png  # Terminal interface preview
├── screenshot-web.png  # Web companion preview
├── screenshot.png      # Project submission thumbnail
├── .gitignore          # Git configuration
├── LICENSE             # MIT License
└── README.md           # Documentation
```

### Design Philosophy
- **Simplicity over abstraction**: No unnecessary frameworks, class hierarchies, or heavy runtime dependencies.
- **Reliability**: Deterministic rules guarantee identical, reproducible outputs every time.
- **Fast Startup**: Loads and responds in sub-millisecond execution times.

---

## Hack Club Chatterbox Compliance

Tavi was built specifically to fulfill the requirements of Hack Club's **Chatterbox**:

- **No AI Models**: No LLMs, OpenAI/Anthropic APIs, neural networks, or weights are loaded or contacted.
- **Rule-Based Engine**: Natural-feeling conversational dialogue driven strictly by deterministic pattern matching and structured intent handlers.
- **Standard Library Only**: Operates without any third-party Python packages.

---

## License

This project is licensed under the [MIT License](LICENSE) — free to inspect, modify, and distribute.
