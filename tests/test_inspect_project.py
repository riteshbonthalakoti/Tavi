import pytest
import os
import json
from pathlib import Path
from tavi.application.service import ApplicationService
from tavi.agent.models import TaskStatus

@pytest.fixture
def temp_project(tmp_path):
    def _create(files):
        for f, content in files.items():
            file_path = tmp_path / f
            file_path.write_text(content)
        return str(tmp_path)
    return _create

def test_inspect_empty_project(temp_project):
    workspace = temp_project({})
    app = ApplicationService(workspace_root=workspace)
    res = app.run_task("inspect_project")
    
    assert res.success is True
    assert res.status == TaskStatus.COMPLETED
    assert res.structured_data["git"]["is_repository"] is False
    assert res.structured_data["project"]["types"] == []
    assert res.structured_data["testing"]["frameworks"] == []

def test_inspect_python_project(temp_project):
    workspace = temp_project({
        "requirements.txt": "pytest==8.0.0\nfastapi",
        "main.py": "print('hello')"
    })
    app = ApplicationService(workspace_root=workspace)
    res = app.run_task("inspect_project")
    
    assert res.success is True
    assert "Python" in res.structured_data["project"]["types"]
    assert "requirements.txt" in res.structured_data["project"]["evidence"]
    assert "pytest" in res.structured_data["testing"]["frameworks"]

def test_inspect_node_project(temp_project):
    workspace = temp_project({
        "package.json": json.dumps({"dependencies": {}, "devDependencies": {"jest": "^29.0"}})
    })
    app = ApplicationService(workspace_root=workspace)
    res = app.run_task("inspect_project")
    
    assert res.success is True
    assert "Node" in res.structured_data["project"]["types"]
    assert "package.json" in res.structured_data["project"]["evidence"]
    assert "jest" in res.structured_data["testing"]["frameworks"]

def test_inspect_invalid_workspace():
    app = ApplicationService(workspace_root="/does/not/exist/12345")
    res = app.run_task("inspect_project")
    
    assert res.success is False
    assert res.status == TaskStatus.FAILED
    assert res.final_state == "FAILURE"
    assert "Workspace root does not exist" in res.error
