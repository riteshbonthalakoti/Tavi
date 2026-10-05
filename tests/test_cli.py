import pytest
import sys
from unittest.mock import MagicMock, patch

# Mock PromptSession at the top level to avoid Win32 console errors during test collection
with patch('prompt_toolkit.PromptSession', MagicMock()):
    from tavi.cli.app import CLIApp

from tavi.application.service import MessageResult
from tavi.agent.models import TaskResult, TaskStatus
from tavi.core.models import Observation

def test_cli_help(capsys):
    app = CLIApp()
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.read", return_value="help\n"):
        app.run()
    
    captured = capsys.readouterr()
    assert "inspect this project" in captured.out

def test_cli_exit():
    app = CLIApp()
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.read", return_value="exit\n"):
        with pytest.raises(SystemExit):
            app.run()

def test_cli_quit():
    app = CLIApp()
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.read", return_value="quit\n"):
        with pytest.raises(SystemExit):
            app.run()

def test_cli_empty_input(capsys):
    app = CLIApp()
    app.app_service = MagicMock()
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.read", return_value="\n   \n"):
        app.run()
    
    app.app_service.handle_message.assert_not_called()

def test_cli_conversation_greeting(capsys):
    app = CLIApp()
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.read", return_value="hello\n"):
        app.run()
    
    captured = capsys.readouterr()
    assert "Hey. I'm Tavi." in captured.out
    assert "What are we working on?" in captured.out

def test_cli_conversation_status(capsys):
    app = CLIApp()
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.read", return_value="how are you?\n"):
        app.run()
    
    captured = capsys.readouterr()
    assert "Running smoothly" in captured.out

def test_cli_conversation_farewell(capsys):
    app = CLIApp()
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.read", return_value="bye\n"):
        app.run()
    
    captured = capsys.readouterr()
    assert "See you" in captured.out

def test_cli_unsupported_request(capsys):
    app = CLIApp()
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.read", return_value="tell me a joke\n"):
        app.run()
    
    captured = capsys.readouterr()
    assert "I don't have a workflow for that yet" in captured.out

def test_cli_conversation_does_not_execute_workflow():
    app = CLIApp()
    with patch.object(app.app_service, "run_task") as mock_run_task:
        for prompt in ["hello", "how are you", "see you", "help"]:
            res = app.app_service.handle_message(prompt)
            assert res.executed is False
            assert res.task_result is None
        mock_run_task.assert_not_called()

def test_cli_task_executes_workflow():
    app = CLIApp()
    with patch.object(app.app_service, "run_task") as mock_run_task:
        mock_run_task.return_value = TaskResult(
            success=True,
            observations=[],
            structured_data={"project": {"types": ["Python"]}},
            error=None,
            duration=0.5,
            final_state="SUCCESS",
            metadata={},
            task_name="inspect_project",
            request_id="test",
            status=TaskStatus.COMPLETED
        )
        res = app.app_service.handle_message("inspect this project")
        assert res.executed is True
        mock_run_task.assert_called_once_with("inspect_project", {})

def test_cli_supported_request(capsys):
    app = CLIApp()
    
    mock_task_result = TaskResult(
        success=True,
        observations=[Observation(kind="test", message="Test step done", source_tool="test")],
        structured_data={
            "project": {"types": ["Python"]},
            "testing": {"frameworks": ["pytest"]},
            "git": {"is_repository": True, "branch": "master", "status": "clean"}
        },
        error=None,
        duration=1.0,
        final_state="SUCCESS",
        metadata={},
        task_name="inspect_project",
        request_id="123",
        status=TaskStatus.COMPLETED
    )
    
    mock_result = MessageResult(
        intent_name="inspect_project",
        confidence=1.0,
        executed=True,
        response_text="Success",
        task_result=mock_task_result
    )
    
    app.app_service = MagicMock()
    app.app_service.handle_message.return_value = mock_result
    
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.read", return_value="inspect this project\n"):
        app.run()
        
    app.app_service.handle_message.assert_called_once_with("inspect this project")
    captured = capsys.readouterr()
    assert "Inspecting workspace" in captured.out
    assert "PROJECT" in captured.out
    assert "Python" in captured.out
    assert "master" in captured.out
    assert "clean" in captured.out

def test_cli_debug_mode(capsys):
    app = CLIApp()
    app.debug = True
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.read", return_value="hello\n"):
        app.run()
    captured = capsys.readouterr()
    assert "[debug]" in captured.out
    assert "intent=greeting" in captured.out

def test_cli_normal_mode_no_debug(capsys):
    app = CLIApp()
    app.debug = False
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.read", return_value="hello\n"):
        app.run()
    captured = capsys.readouterr()
    assert "[debug]" not in captured.out
    assert "Intent recognized" not in captured.out

def test_cli_continuous_conversation(capsys):
    app = CLIApp()
    inputs = "hello\nhow are you\ntell me a joke\n"
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.read", return_value=inputs):
        app.run()
    captured = capsys.readouterr()
    # Header printed only once
    assert captured.out.count("TAVI · LOCAL AGENT") == 1
    # All responses present
    assert "Hey. I'm Tavi." in captured.out
    assert "Running smoothly" in captured.out
    assert "I don't have a workflow for that yet" in captured.out

def test_cli_clear(capsys):
    app = CLIApp()
    app.renderer.clear = MagicMock()
    
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.read", return_value="clear\n"):
        app.run()
        
    app.renderer.clear.assert_called_once()
