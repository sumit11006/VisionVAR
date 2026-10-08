import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_gemini_assistant_no_api_key():
    import os
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    
    res = client.post("/api/assistant/chat", json={
        "message": "What is the match summary?",
        "match_id": "test_match_123"
    })
    
    assert res.status_code == 200
    data = res.json()
    assert "GEMINI_API_KEY is not set" in data["response"]
