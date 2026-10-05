import pytest
from fastapi.testclient import TestClient
from tavi.web.api import app
from tavi.conversation.engine import ConversationEngine

client = TestClient(app)

def test_engine_echo():
    engine = ConversationEngine()
    response = engine.process_message("Hello", "test_session")
    assert response == "Tavi heard: Hello"

def test_web_endpoint():
    response = client.post("/api/chat", json={"text": "Hi Tavi", "session_id": "123"})
    assert response.status_code == 200
    assert response.json() == {"response": "Tavi heard: Hi Tavi"}

def test_index_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
