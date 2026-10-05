from tavi.agent.workflow import BaseWorkflow, StateHandler
from tavi.agent.models import TaskContext
from tavi.security.permissions import PermissionMiddleware
from tavi.core.models import ToolRequest, Observation
import json

class InspectProjectWorkflow(BaseWorkflow):
    @property
    def name(self) -> str:
        return "inspect_project"

    def register_states(self) -> None:
        self.add_state("START", self._state_start)
        self.add_state("VALIDATE_WORKSPACE", self._state_validate_workspace)
        self.add_state("CHECK_GIT", self._state_check_git)
        self.add_state("GET_BRANCH", self._state_get_branch)
        self.add_state("GET_GIT_STATUS", self._state_get_git_status)
        self.add_state("LIST_PROJECT_ROOT", self._state_list_project_root)
        self.add_state("DETECT_PROJECT_TYPE", self._state_detect_project_type)
        self.add_state("DETECT_TEST_FRAMEWORK", self._state_detect_test_framework)
        self.add_state("BUILD_RESULT", self._state_build_result)

    def _state_start(self, context: TaskContext, middleware: PermissionMiddleware) -> str:
        context.structured_data = {
            "workspace_root": context.request.workspace_root,
            "git": {"is_repository": False},
            "project": {"types": [], "evidence": []},
            "testing": {"frameworks": []}
        }
        return "VALIDATE_WORKSPACE"

    def _state_validate_workspace(self, context: TaskContext, middleware: PermissionMiddleware) -> str:
        req = ToolRequest(
            tool_name="filesystem",
            arguments={"operation": "directory_exists", "path": "."},
            request_id=f"{context.request.request_id}-val"
        )
        res = middleware.execute_request(req)
        
        if not res.success or not res.output:
            context.structured_data["error_reason"] = "Workspace root does not exist or is inaccessible."
            return "FAILURE"
            
        context.observations.append(Observation(
            kind="WorkspaceValidated", 
            message="Workspace directory exists and is accessible.",
            source_tool="filesystem"
        ))
        return "CHECK_GIT"

    def _state_check_git(self, context: TaskContext, middleware: PermissionMiddleware) -> str:
        req = ToolRequest(
            tool_name="git",
            arguments={"operation": "status"},
            request_id=f"{context.request.request_id}-git-check"
        )
        res = middleware.execute_request(req)
        
        if not res.success:
            context.observations.append(Observation(
                kind="GitRepositoryNotDetected",
                message="Directory is not a Git repository.",
                source_tool="git"
            ))
            return "LIST_PROJECT_ROOT"
            
        context.structured_data["git"]["is_repository"] = True
        context.observations.append(Observation(
            kind="GitRepositoryDetected",
            message="Git repository detected.",
            source_tool="git"
        ))
        return "GET_BRANCH"

    def _state_get_branch(self, context: TaskContext, middleware: PermissionMiddleware) -> str:
        req = ToolRequest(
            tool_name="git",
            arguments={"operation": "current_branch"},
            request_id=f"{context.request.request_id}-git-branch"
        )
        res = middleware.execute_request(req)
        if res.success:
            context.structured_data["git"]["branch"] = res.output
            context.observations.append(Observation(
                kind="GitBranchDetected",
                message=f"Current branch: {res.output}",
                source_tool="git"
            ))
        return "GET_GIT_STATUS"

    def _state_get_git_status(self, context: TaskContext, middleware: PermissionMiddleware) -> str:
        req = ToolRequest(
            tool_name="git",
            arguments={"operation": "status"},
            request_id=f"{context.request.request_id}-git-status"
        )
        res = middleware.execute_request(req)
        if res.success:
            is_clean = "working tree clean" in res.output
            context.structured_data["git"]["status"] = "clean" if is_clean else "dirty"
            context.observations.append(Observation(
                kind="GitStatusCollected",
                message="Clean" if is_clean else "Dirty",
                source_tool="git"
            ))
        return "LIST_PROJECT_ROOT"

    def _state_list_project_root(self, context: TaskContext, middleware: PermissionMiddleware) -> str:
        req = ToolRequest(
            tool_name="filesystem",
            arguments={"operation": "list_directory", "path": "."},
            request_id=f"{context.request.request_id}-ls"
        )
        res = middleware.execute_request(req)
        if not res.success:
            context.structured_data["error_reason"] = "Failed to list project root."
            return "FAILURE"
            
        files = res.output
        context.structured_data["_raw_files"] = files
        context.observations.append(Observation(
            kind="ProjectFilesDetected",
            message=f"Detected {len(files)} files/directories in root.",
            source_tool="filesystem"
        ))
        return "DETECT_PROJECT_TYPE"

    def _state_detect_project_type(self, context: TaskContext, middleware: PermissionMiddleware) -> str:
        files = set(context.structured_data.get("_raw_files", []))
        types = []
        evidence = []
        
        # Python
        py_evidence = {"pyproject.toml", "requirements.txt", "setup.py", "setup.cfg"}.intersection(files)
        if py_evidence:
            types.append("Python")
            evidence.extend(list(py_evidence))
            
        # Node
        if "package.json" in files:
            types.append("Node")
            evidence.append("package.json")
            
        # Rust
        if "Cargo.toml" in files:
            types.append("Rust")
            evidence.append("Cargo.toml")
            
        # Go
        if "go.mod" in files:
            types.append("Go")
            evidence.append("go.mod")
            
        # Java
        java_evidence = {"pom.xml", "build.gradle", "build.gradle.kts"}.intersection(files)
        if java_evidence:
            types.append("Java")
            evidence.extend(list(java_evidence))

        context.structured_data["project"]["types"] = types
        context.structured_data["project"]["evidence"] = evidence
        
        context.observations.append(Observation(
            kind="ProjectTypeDetected",
            message=f"Types: {', '.join(types) if types else 'Unknown'}",
            source_tool="agent"
        ))
        
        return "DETECT_TEST_FRAMEWORK"

    def _state_detect_test_framework(self, context: TaskContext, middleware: PermissionMiddleware) -> str:
        files = set(context.structured_data.get("_raw_files", []))
        frameworks = []
        
        # Pytest
        if "pytest.ini" in files:
            frameworks.append("pytest")
        elif "requirements.txt" in files:
            # Check inside requirements.txt
            req = ToolRequest(
                tool_name="filesystem",
                arguments={"operation": "read_file", "path": "requirements.txt"},
                request_id=f"{context.request.request_id}-read-req"
            )
            res = middleware.execute_request(req)
            if res.success and "pytest" in res.output.lower():
                frameworks.append("pytest")
                
        # Javascript (naive check in package.json)
        if "package.json" in files:
            req = ToolRequest(
                tool_name="filesystem",
                arguments={"operation": "read_file", "path": "package.json"},
                request_id=f"{context.request.request_id}-read-pkg"
            )
            res = middleware.execute_request(req)
            if res.success:
                try:
                    pkg = json.loads(res.output)
                    deps = str(pkg.get("devDependencies", {})) + str(pkg.get("dependencies", {}))
                    if "jest" in deps:
                        frameworks.append("jest")
                    if "vitest" in deps:
                        frameworks.append("vitest")
                except json.JSONDecodeError:
                    pass

        context.structured_data["testing"]["frameworks"] = list(set(frameworks))
        context.observations.append(Observation(
            kind="TestFrameworkDetected",
            message=f"Frameworks: {', '.join(frameworks) if frameworks else 'Unknown'}",
            source_tool="agent"
        ))
        return "BUILD_RESULT"

    def _state_build_result(self, context: TaskContext, middleware: PermissionMiddleware) -> str:
        # Cleanup raw files from output
        if "_raw_files" in context.structured_data:
            del context.structured_data["_raw_files"]
        return "SUCCESS"
