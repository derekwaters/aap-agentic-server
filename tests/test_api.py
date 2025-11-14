"""Test cases for the AAP Agentic Server API."""
import pytest
import asyncio
import httpx
from app.api import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_send_chat_and_get_complete_response(client):
    """
    Test Case 1: Use send_chat to send 'What model are you?'. 
    Use get_chat calls to retrieve the output, and verify that 
    a response eventually receives the chat_complete value as true.
    """
    # Send chat message
    send_response = client.post(
        "/api/send_chat",
        json={"text": "What model are you?"}
    )
    assert send_response.status_code == 200
    session_id = send_response.json()["session_id"]
    assert session_id is not None
    
    # Poll get_chat until chat_complete is true
    max_attempts = 30
    attempt = 0
    chat_complete = False
    
    while not chat_complete and attempt < max_attempts:
        get_response = client.post(
            "/api/get_chat",
            json={"session_id": session_id}
        )
        assert get_response.status_code == 200
        data = get_response.json()
        
        assert "response" in data
        assert "chat_complete" in data
        
        chat_complete = data["chat_complete"]
        attempt += 1
        
        if not chat_complete:
            # Wait a bit before next poll
            import time
            time.sleep(0.5)
    
    # Verify that we eventually got a complete response
    assert chat_complete, "Chat did not complete within expected time"
    assert len(data["response"]) > 0, "Response should not be empty"


def test_get_chat_after_completion(client):
    """
    Test Case 2: Repeat the first test, but make a request to get_chat 
    after chat_complete is true. Verify that no error results.
    """
    # Send chat message
    send_response = client.post(
        "/api/send_chat",
        json={"text": "What model are you?"}
    )
    assert send_response.status_code == 200
    session_id = send_response.json()["session_id"]
    
    # Poll until complete
    max_attempts = 30
    attempt = 0
    chat_complete = False
    
    while not chat_complete and attempt < max_attempts:
        get_response = client.post(
            "/api/get_chat",
            json={"session_id": session_id}
        )
        assert get_response.status_code == 200
        data = get_response.json()
        chat_complete = data["chat_complete"]
        attempt += 1
        
        if not chat_complete:
            import time
            time.sleep(0.5)
    
    assert chat_complete, "Chat should complete"
    
    # Now make another get_chat request after completion
    get_response = client.post(
        "/api/get_chat",
        json={"session_id": session_id}
    )
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["chat_complete"] is True
    assert "response" in data


def test_multiple_sessions_concurrent(client):
    """
    Test Case 3: Use send_chat to send 'What model are you?'. 
    Before calling get_chat, use send_chat to send another request 
    with 'What is the capital of China?'. Call get_chat with the 
    first session_id and verify that results are received.
    """
    # Send first chat message
    send_response1 = client.post(
        "/api/send_chat",
        json={"text": "What model are you?"}
    )
    assert send_response1.status_code == 200
    session_id1 = send_response1.json()["session_id"]
    
    # Send second chat message before calling get_chat on first
    send_response2 = client.post(
        "/api/send_chat",
        json={"text": "What is the capital of China?"}
    )
    assert send_response2.status_code == 200
    session_id2 = send_response2.json()["session_id"]
    
    # Verify sessions are different
    assert session_id1 != session_id2
    
    # Now call get_chat with the first session_id
    get_response = client.post(
        "/api/get_chat",
        json={"session_id": session_id1}
    )
    assert get_response.status_code == 200
    data = get_response.json()
    assert "response" in data
    assert "chat_complete" in data
    
    # Poll until first session completes
    max_attempts = 30
    attempt = 0
    chat_complete = False
    
    while not chat_complete and attempt < max_attempts:
        get_response = client.post(
            "/api/get_chat",
            json={"session_id": session_id1}
        )
        assert get_response.status_code == 200
        data = get_response.json()
        chat_complete = data["chat_complete"]
        attempt += 1
        
        if not chat_complete:
            import time
            time.sleep(0.5)
    
    assert chat_complete, "First session should complete"
    assert len(data["response"]) > 0, "Response should not be empty"

