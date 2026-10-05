import os
import sys
from rich.console import Console
from tavi.cli.theme import tavi_theme
from tavi.agent.models import TaskResult

def _supports_utf8() -> bool:
    try:
        encoding = getattr(sys.stdout, "encoding", "utf-8") or "utf-8"
        "✓".encode(encoding)
        return True
    except (UnicodeEncodeError, LookupError):
        return False

class CLIRenderer:
    def __init__(self):
        self.console = Console(theme=tavi_theme)
        utf8 = _supports_utf8()
        self.sym_check = "✓" if utf8 else "+"
        self.sym_cross = "x"
        self.sym_branch = "├─" if utf8 else "|--"
        self.sym_last = "└─" if utf8 else "\\--"
        self.sym_divider = "─" if utf8 else "-"

    def print_header(self):
        self.console.print("\n[tavi.header]TAVI[/] [tavi.dim]·[/] [tavi.dim]LOCAL AGENT[/]\n")

    def print_tavi_response(self, text: str):
        lines = text.strip().split("\n")
        self.console.print()
        for line in lines:
            self.console.print(f"  [tavi.text]{line}[/]")
        self.console.print()

    def print_error(self, message: str, diagnostic: str = None):
        self.console.print(f"\n  [tavi.error]{self.sym_cross} {message}[/]")
        if diagnostic:
            self.console.print(f"  [tavi.dim]{diagnostic}[/]")
        self.console.print()

    def print_debug(self, intent_name: str, confidence: float):
        self.console.print(f"\n  [tavi.dim]\\[debug] intent={intent_name} confidence={confidence:.1f}[/]\n")

    def render_result(self, result: TaskResult, intent_name: str):
        if not result.success:
            self.print_error("Workflow failed.", diagnostic=result.error)
            return

        if intent_name == "inspect_project":
            self._render_project_inspection(result)
        else:
            self.console.print(f"\n  [tavi.symbol]{self.sym_check}[/] [tavi.text]Task completed successfully.[/]\n")

    def _render_project_inspection(self, result: TaskResult):
        sd = result.structured_data or {}
        git_info = sd.get("git", {})
        proj_types = sd.get("project", {}).get("types", [])
        test_frameworks = sd.get("testing", {}).get("frameworks", [])

        self.console.print("\n  [tavi.text]Inspecting workspace[/]")
        self.console.print(f"  [tavi.dim]{self.sym_divider * 29}[/]\n")

        # Real observations
        if git_info.get("is_repository"):
            self.console.print(f"  [tavi.symbol]{self.sym_check}[/] [tavi.text]Git repository[/]")
        else:
            self.console.print(f"  [tavi.dim]- No Git repository detected[/]")

        if proj_types:
            for p in proj_types:
                self.console.print(f"  [tavi.symbol]{self.sym_check}[/] [tavi.text]{p} project[/]")
        else:
            self.console.print(f"  [tavi.dim]- Unknown project type[/]")

        if test_frameworks:
            for tf in test_frameworks:
                self.console.print(f"  [tavi.symbol]{self.sym_check}[/] [tavi.text]{tf} detected[/]")
        else:
            self.console.print(f"  [tavi.dim]- No test framework detected[/]")

        # Compact tree summary
        items = []
        for p in proj_types:
            items.append(p)
        for tf in test_frameworks:
            items.append(tf)
        if git_info.get("is_repository"):
            branch = git_info.get("branch")
            if branch:
                items.append(branch)
            status = git_info.get("status", "unknown")
            items.append(status)

        if items:
            self.console.print(f"\n  [tavi.label]PROJECT[/]")
            for i, item in enumerate(items):
                branch_char = self.sym_last if i == len(items) - 1 else self.sym_branch
                self.console.print(f"  [tavi.branch]{branch_char}[/] [tavi.value]{item}[/]")

        self.console.print()

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_header()
