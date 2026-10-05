import pytest
from tavi.agent.intent import IntentRegistry, IntentEngine, IntentResult
from tavi.application.service import ApplicationService
from tavi.agent.models import TaskResult

@pytest.fixture
def intent_engine():
    registry = IntentRegistry()
    registry.register("inspect_project", [
        r"^(can you\s+)?(please\s+)?inspect (this\s+)?project$",
        r"^(can you\s+)?(please\s+)?analyze (this\s+)?project$",
        r"^(can you\s+)?(please\s+)?analyze (this\s+)?repository$",
        r"^(can you\s+)?(please\s+)?check (this\s+)?project$",
        r"^(can you\s+)?(please\s+)?check (this\s+)?repository$",
        r"^(can you\s+)?(please\s+)?show project structure$"
    ])
    return IntentEngine(registry)

def test_normalization(intent_engine):
    assert intent_engine.normalize("Inspect This Project!") == "inspect this project"
    assert intent_engine.normalize(" inspect   this   project ") == "inspect this project"
    assert intent_engine.normalize("INSPECT THIS PROJECT") == "inspect this project"
    assert intent_engine.normalize("Can you inspect this project?") == "can you inspect this project"

def test_exact_matching(intent_engine):
    res = intent_engine.classify("inspect project")
    assert res.is_supported is True
    assert res.intent_name == "inspect_project"
    assert res.confidence == 1.0

def test_variants_matching(intent_engine):
    variants = [
        "inspect this project",
        "analyze this repository",
        "check this project",
        "show project structure"
    ]
    for v in variants:
        res = intent_engine.classify(v)
        assert res.is_supported is True
        assert res.intent_name == "inspect_project"

def test_case_insensitivity(intent_engine):
    res = intent_engine.classify("INSPECT THIS PROJECT")
    assert res.is_supported is True
    assert res.intent_name == "inspect_project"

def test_punctuation(intent_engine):
    res = intent_engine.classify("Can you inspect this project?")
    assert res.is_supported is True
    assert res.intent_name == "inspect_project"

def test_false_positives(intent_engine):
    negatives = [
        "I like projects",
        "Tell me about project management",
        "project"
    ]
    for n in negatives:
        res = intent_engine.classify(n)
        assert res.is_supported is False
        assert res.intent_name is None
        assert res.confidence == 0.0

def test_unsupported_request(intent_engine):
    res = intent_engine.classify("tell me a joke")
    assert res.is_supported is False
    assert res.intent_name is None
    assert res.confidence == 0.0

from tavi.application.service import ApplicationService, MessageResult

def test_application_integration():
    app = ApplicationService()
    # Mock or trust the default environment
    result = app.handle_message("inspect this project")
    assert isinstance(result, MessageResult)
    assert result.intent_name == "inspect_project"
    assert result.confidence == 1.0
    assert result.executed is True
    assert result.task_result is not None
    assert result.task_result.task_name == "inspect_project"
    assert "completed successfully" in result.response_text or "failed" in result.response_text
    
    # Unsupported
    unsupported_result = app.handle_message("tell me a joke")
    assert isinstance(unsupported_result, MessageResult)
    assert unsupported_result.intent_name is None
    assert unsupported_result.confidence == 0.0
    assert unsupported_result.executed is False
    assert unsupported_result.task_result is None
    assert "don't have a supported workflow" in unsupported_result.response_text
