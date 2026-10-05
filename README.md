# Tavi

Tavi is a small, local personal agent designed to run interactively in your terminal and via a lightweight web interface.

## Running Tavi

### Terminal

Run the interactive terminal interface:

```bash
python tavi.py
```

Type naturally to interact, inspect projects, or exit:

```text
› hello
› what can you do for me?
› inspect this project
› exit
```

### Web Interface

Start the local web server:

```bash
python web.py
```

Then open `http://localhost:8000` in your browser.

## Capabilities

- Natural deterministic conversational handling (greetings, status, capabilities, activity queries, help)
- Local workspace and Git repository inspection
- Project type detection (Python, Node, Rust, Go, Java)
- Test setup detection (pytest)
- Read-only Git branch and working tree state reporting

## Architecture

- `tavi.py`: Core intent classification, deterministic conversation responses, project inspection, and terminal interface.
- `web.py`: Standard library HTTP server exposing `index.html` and a `/chat` JSON endpoint.
- `index.html`: Standalone single-page web interface with vanilla HTML, CSS, and JavaScript.

No external packages, no LLMs, and no build steps are required.

## Crescent Compliance

Tavi operates completely deterministically using the Python standard library. It does not use runtime language models, remote AI APIs, or third-party inference services.
