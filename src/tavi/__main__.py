import sys
from tavi.application.service import ApplicationService

def main():
    print("=" * 50)
    print("TAVI")
    print("Local Personal Agent")
    print("=" * 50)
    
    app = ApplicationService()
    
    # Process standard input if piped, otherwise interactive
    if not sys.stdin.isatty():
        lines = sys.stdin.read().splitlines()
        for user_input in lines:
            if not user_input.strip():
                continue
            print(f"\nYou > {user_input}")
            process_input(app, user_input)
        return

    try:
        while True:
            try:
                user_input = input("\nYou > ")
                if user_input.strip().lower() in ("exit", "quit"):
                    break
                if not user_input.strip():
                    continue
                process_input(app, user_input)
            except EOFError:
                break
    except KeyboardInterrupt:
        pass
    print("\nGoodbye!")

def process_input(app: ApplicationService, user_input: str):
    result = app.handle_message(user_input)
    
    print(f"\nIntent: {result.intent_name or 'UNKNOWN'}")
    print(f"Confidence: {result.confidence:.1f}")
    
    if result.executed and result.task_result:
        tr = result.task_result
        if tr.success:
            sd = tr.structured_data
            print("\nProject:")
            
            proj_types = sd.get("project", {}).get("types", [])
            print(f"  Type: {', '.join(proj_types) if proj_types else 'Unknown'}")
            
            test_frameworks = sd.get("testing", {}).get("frameworks", [])
            print(f"  Test framework: {', '.join(test_frameworks) if test_frameworks else 'None'}")
            
            git_info = sd.get("git", {})
            print(f"  Git repository: {'yes' if git_info.get('is_repository') else 'no'}")
            
            if git_info.get('is_repository'):
                branch = git_info.get('branch', 'unknown')
                print(f"  Branch: {branch}")
                
                status_raw = git_info.get('status', '').strip()
                status_display = "clean"
                if status_raw:
                    # Just count lines or show brief summary
                    status_lines = len(status_raw.split('\n'))
                    status_display = f"{status_lines} pending change(s)"
                print(f"  Git status: {status_display}")
        else:
            print(f"\nTask failed: {tr.error}")
    else:
        print(f"\nTavi: {result.response_text}")

if __name__ == "__main__":
    main()
