import os
import sys
import re
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

CYAN = "\033[36m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
RESET = "\033[0m"

def normalize(text: str) -> str:
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return " ".join(cleaned.split())

def classify(text: str) -> str:
    normalized = normalize(text)
    if not normalized:
        return "empty"

    if re.search(r"^(hi|hello|hey|good morning|good afternoon|good evening)(\s+tavi)?$", normalized):
        return "greeting"

    if re.search(r"^(how are you|how are you doing|you okay|hows it going|how are things)(\s+tavi)?$", normalized):
        return "status"

    if re.search(r"^(what are you doing|what are you working on|what are you up to)(\s+tavi)?$", normalized):
        return "activity"

    if re.search(r"^(what can you do|what can you do for me|what do you do|what are your capabilities|capabilities|features)(\s+tavi)?$", normalized):
        return "capabilities"

    if re.search(r"^(tell me a joke|joke)$", normalized):
        return "joke"

    if re.search(r"^(bye|goodbye|see you|good night)(\s+tavi)?$", normalized):
        return "farewell"

    if re.search(r"^(can you\s+)?(please\s+)?(inspect|analyze|check)\s+(this|your|my)?\s*(project|repository)$", normalized):
        return "inspect_project"

    if re.search(r"^(help|commands|how do i use this)$", normalized):
        return "help"

    if normalized in ("clear", "cls"):
        return "clear"

    if normalized in ("exit", "quit", "q"):
        return "exit"

    return "unknown"

def check_symbol() -> str:
    try:
        encoding = getattr(sys.stdout, "encoding", "") or "utf-8"
        "✓".encode(encoding)
        return "✓"
    except Exception:
        return "+"

def inspect_project(workspace_dir: str = ".") -> str:
    root = Path(workspace_dir).resolve()
    sym = check_symbol()
    facts = []
    summary_parts = []

    is_git = False
    branch = ""
    git_status = ""

    try:
        git_check = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )
        is_git = git_check.returncode == 0 and git_check.stdout.strip() == "true"
    except Exception:
        is_git = False

    if is_git:
        facts.append(f"{sym} Git repository")
        try:
            branch_cmd = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
            )
            branch = branch_cmd.stdout.strip()
        except Exception:
            branch = ""

        try:
            status_cmd = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
            )
            git_status = "clean" if len(status_cmd.stdout.strip()) == 0 else "dirty"
        except Exception:
            git_status = ""

    project_types = []
    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists() or (root / "setup.py").exists() or (root / "tavi.py").exists():
        project_types.append("Python")
    if (root / "package.json").exists():
        project_types.append("Node")
    if (root / "Cargo.toml").exists():
        project_types.append("Rust")
    if (root / "go.mod").exists():
        project_types.append("Go")
    if (root / "pom.xml").exists() or (root / "build.gradle").exists():
        project_types.append("Java")

    for p in project_types:
        facts.append(f"{sym} {p} project")
        summary_parts.append(p)

    test_frameworks = []
    has_pytest = (root / "pytest.ini").exists()
    if not has_pytest and (root / "pyproject.toml").exists():
        try:
            content = (root / "pyproject.toml").read_text(encoding="utf-8", errors="ignore")
            if "pytest" in content:
                has_pytest = True
        except Exception:
            pass

    if has_pytest:
        test_frameworks.append("pytest")

    for t in test_frameworks:
        facts.append(f"{sym} {t} detected")
        summary_parts.append(t)

    if branch:
        summary_parts.append(branch)
    if git_status:
        summary_parts.append(git_status)

    output = ["Inspecting workspace\n"]
    for fact in facts:
        output.append(f"  {fact}")

    if summary_parts:
        output.append("\n  PROJECT")
        output.append("  " + " · ".join(summary_parts))

    return "\n".join(output)

def respond(message: str, workspace_dir: str = ".") -> str:
    intent = classify(message)

    if intent == "greeting":
        return "Hey. I'm Tavi.\nWhat are we working on?"
    if intent == "status":
        return "Running smoothly.\nWhat should we work on?"
    if intent == "activity":
        return "I'm here and ready.\nI can currently inspect your project and repository."
    if intent == "capabilities":
        return "I can inspect your project, repository, Git state, and test setup."
    if intent == "joke":
        return "I can't do that one yet.\nI'm currently focused on project work."
    if intent == "farewell":
        return "See you."
    if intent == "help":
        return "I can inspect your project, repository, Git state, and test setup.\n\nTry:\n  inspect this project"
    if intent == "inspect_project":
        return inspect_project(workspace_dir)

    return "I can help with project work right now.\nTry asking me to inspect your project."

def render_banner(workspace_dir: str = "."):
    root = Path(workspace_dir).resolve()
    git_info = "not a git repo"
    try:
        res = subprocess.run(["git", "branch", "--show-current"], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
        if res.returncode == 0 and res.stdout.strip():
            status = subprocess.run(["git", "status", "--porcelain"], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False).stdout.strip()
            state = "clean" if len(status) == 0 else "dirty"
            git_info = f"{res.stdout.strip()} ({state})"
    except Exception:
        pass

    ws_str = str(root)
    if len(ws_str) > 52:
        ws_str = "..." + ws_str[-49:]

    print()
    print(f"{CYAN}  ████████╗ █████╗ ██╗   ██╗██╗{RESET}")
    print(f"{CYAN}  ╚══██╔══╝██╔══██╗██║   ██║██║   {BOLD}T A V I{RESET}  {DIM}v0.4.0{RESET}")
    print(f"{CYAN}     ██║   ███████║██║   ██║██║   {DIM}Local Personal Workspace Agent{RESET}")
    print(f"{CYAN}     ██║   ██╔══██║╚██╗ ██╔╝██║{RESET}")
    print(f"{CYAN}     ██║   ██║  ██║ ╚████╔╝ ██║   {GREEN}● local · ready{RESET}")
    print(f"{CYAN}     ╚═╝   ╚═╝  ╚═╝  ╚═══╝  ╚═╝{RESET}")
    print()
    print(f"{DIM}╭────────────────────────────────────────────────────────────────────────╮{RESET}")
    print(f"{DIM}│{RESET}  {BOLD}Workspace:{RESET}  {ws_str:<56} {DIM}│{RESET}")
    print(f"{DIM}│{RESET}  {BOLD}Git State:{RESET}  {git_info:<56} {DIM}│{RESET}")
    print(f"{DIM}│{RESET}  {BOLD}Engine:{RESET}     {'Deterministic Local Engine':<56} {DIM}│{RESET}")
    print(f"{DIM}├────────────────────────────────────────────────────────────────────────┤{RESET}")
    print(f"{DIM}│{RESET}  {BOLD}Quick Commands:{RESET}                                                        {DIM}│{RESET}")
    print(f"{DIM}│{RESET}    {CYAN}inspect this project{RESET}  Inspect git, project structure, and tests      {DIM}│{RESET}")
    print(f"{DIM}│{RESET}    {CYAN}what can you do?{RESET}      View capabilities & features                   {DIM}│{RESET}")
    print(f"{DIM}│{RESET}    {CYAN}help{RESET}                  Show command reference                         {DIM}│{RESET}")
    print(f"{DIM}│{RESET}    {CYAN}clear{RESET}                 Clear session buffer                           {DIM}│{RESET}")
    print(f"{DIM}│{RESET}    {CYAN}exit{RESET}                  Exit session                                   {DIM}│{RESET}")
    print(f"{DIM}╰────────────────────────────────────────────────────────────────────────╯{RESET}")
    print()

def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if os.name == "nt":
        os.system("")

    render_banner()

    while True:
        try:
            user_input = input(f"{CYAN}›{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{CYAN}Tavi{RESET}\nSee you.\n")
            break

        if not user_input:
            continue

        intent = classify(user_input)
        if intent == "exit":
            print(f"\n{CYAN}Tavi{RESET}\nSee you.\n")
            break
        if intent == "clear":
            os.system("cls" if os.name == "nt" else "clear")
            render_banner()
            continue

        print(f"\n{DIM}──────────────────────────────────────────────────────────────────────────{RESET}")
        print(f"{BOLD}You ›{RESET} {user_input}")
        print(f"{DIM}──────────────────────────────────────────────────────────────────────────{RESET}")

        reply = respond(user_input)
        print(f"{CYAN}Tavi ›{RESET}")
        print(f"{reply}\n")

if __name__ == "__main__":
    main()
