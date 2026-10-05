from typing import Dict, List
from tavi.agent.workflow import BaseWorkflow

class WorkflowRegistry:
    def __init__(self):
        self._workflows: Dict[str, BaseWorkflow] = {}

    def register(self, workflow: BaseWorkflow) -> None:
        if workflow.name in self._workflows:
            raise ValueError(f"Workflow '{workflow.name}' is already registered.")
        self._workflows[workflow.name] = workflow

    def get_workflow(self, name: str) -> BaseWorkflow:
        if name not in self._workflows:
            raise KeyError(f"Workflow '{name}' not found.")
        return self._workflows[name]

    def list_workflows(self) -> List[str]:
        return list(self._workflows.keys())
