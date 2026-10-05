import sys
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from tavi.application.service import ApplicationService
from tavi.cli.renderer import CLIRenderer

class CLIApp:
    def __init__(self):
        # Configure standard output to utf-8 if supported
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

        self.app_service = ApplicationService()
        self.renderer = CLIRenderer()
        self.style = Style.from_dict({
            'prompt': 'ansicyan',
        })
        self.session = None
        self.debug = os.environ.get("TAVI_DEBUG") == "1"

    def run(self):
        self.renderer.print_header()

        if not sys.stdin.isatty():
            self._run_piped()
            return
            
        self.session = PromptSession(style=self.style)
        
        while True:
            try:
                user_input = self.session.prompt("› ").strip()
                if not user_input:
                    continue
                    
                if self._handle_builtin(user_input):
                    continue
                    
                self._process_input(user_input)
                
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                self.renderer.print_error("Something went wrong while processing the request.", str(e))
                
        self.renderer.console.print("\n  [tavi.dim]See you.[/]\n")

    def _run_piped(self):
        lines = sys.stdin.read().splitlines()
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            self.renderer.console.print(f"› {line_str}")
            if self._handle_builtin(line_str):
                continue
            self._process_input(line_str)

    def _handle_builtin(self, user_input: str) -> bool:
        cmd = user_input.lower()
        if cmd in ("exit", "quit"):
            sys.exit(0)
        if cmd == "clear":
            self.renderer.clear()
            return True
        return False

    def _process_input(self, user_input: str):
        result = self.app_service.handle_message(user_input)
        
        if self.debug:
            self.renderer.print_debug(
                intent_name=result.intent_name or "none",
                confidence=result.confidence
            )

        if not result.executed:
            self.renderer.print_tavi_response(result.response_text)
            return
            
        if result.task_result:
            self.renderer.render_result(result.task_result, result.intent_name)
