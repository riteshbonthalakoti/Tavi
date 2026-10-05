import pytest
from tavi.agent.models import TaskRequest, TaskContext, TaskStatus
from tavi.agent.workflow import BaseWorkflow
from tavi.agent.registry import WorkflowRegistry
from tavi.agent.engine import AgentEngine
from tavi.tools.registry import ToolRegistry
from tavi.security.policy import PermissionPolicy
from tavi.security.permissions import PermissionMiddleware

class DummyWorkflow(BaseWorkflow):
    @property
    def name(self) -> str:
        return "dummy_task"
        
    def register_states(self) -> None:
        self.add_state("START", self._start)
        self.add_state("DO_WORK", self._work)
        self.add_state("LOOP", self._loop)
        
    def _start(self, ctx, mid):
        ctx.structured_data["visited"] = ["START"]
        return "DO_WORK"
        
    def _work(self, ctx, mid):
        ctx.structured_data["visited"].append("DO_WORK")
        if ctx.request.arguments.get("fail_here"):
            return "FAILURE"
        if ctx.request.arguments.get("loop"):
            return "LOOP"
        return "SUCCESS"
        
    def _loop(self, ctx, mid):
        return "DO_WORK"

def setup_engine():
    wf_reg = WorkflowRegistry()
    wf_reg.register(DummyWorkflow())
    
    t_reg = ToolRegistry()
    mid = PermissionMiddleware(t_reg, PermissionPolicy())
    return AgentEngine(wf_reg, mid)

def test_workflow_registry():
    reg = WorkflowRegistry()
    wf = DummyWorkflow()
    reg.register(wf)
    
    with pytest.raises(ValueError):
        reg.register(wf)
        
    assert reg.get_workflow("dummy_task") == wf
    with pytest.raises(KeyError):
        reg.get_workflow("missing")

def test_agent_successful_task():
    engine = setup_engine()
    req = TaskRequest(task_name="dummy_task", workspace_root=".", request_id="1")
    res = engine.execute_task(req)
    
    assert res.success is True
    assert res.status == TaskStatus.COMPLETED
    assert res.final_state == "SUCCESS"
    assert res.structured_data["visited"] == ["START", "DO_WORK"]

def test_agent_failed_task():
    engine = setup_engine()
    req = TaskRequest(task_name="dummy_task", workspace_root=".", arguments={"fail_here": True}, request_id="2")
    res = engine.execute_task(req)
    
    assert res.success is False
    assert res.status == TaskStatus.FAILED
    assert res.final_state == "FAILURE"

def test_agent_unknown_task():
    engine = setup_engine()
    req = TaskRequest(task_name="unknown_task", workspace_root=".", request_id="3")
    res = engine.execute_task(req)
    
    assert res.success is False
    assert res.status == TaskStatus.FAILED
    assert "Failed to resolve workflow" in res.error

def test_agent_transition_limit():
    engine = setup_engine()
    req = TaskRequest(task_name="dummy_task", workspace_root=".", arguments={"loop": True}, request_id="4")
    res = engine.execute_task(req)
    
    assert res.success is False
    assert res.status == TaskStatus.FAILED
    assert "Maximum workflow transitions exceeded" in res.error
