"""REST API endpoints for the AAP Agentic Server."""
import asyncio
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from app.models import (
    SendChatRequest,
    SendChatResponse,
    GetChatRequest,
    GetChatResponse
)
from app.session_manager import SessionManager
from app.agent_service import AgentService

app = FastAPI(title="AAP Agentic Server", version="1.0.0")

# Initialise the agent configuration
load_dotenv(override=True)

base_url = os.getenv("LLAMASTACK_URL", "http://0.0.0.0:8321")
aap_mcp_url = os.getenv("REMOTE_AAP_MCP_URL")
model_id = os.getenv("LLAMASTACK_MODEL_ID", "ollama/qwen3:4b")
# Initialize session manager and agent service
session_manager = SessionManager()
agent_service = AgentService(session_manager, base_url, aap_mcp_url, model_id)


@app.post("/api/send_chat", response_model=SendChatResponse)
async def send_chat(request: SendChatRequest):
    """
    Send a chat message to the AI Agent.
    
    This endpoint creates a new agent session and submits the message
    asynchronously. Returns the session_id for tracking the conversation.
    """
    # Create a new session
    session_id = session_manager.create_session()
    
    # Start the agent turn asynchronously in the background
    # Don't await - let it run in the background
    asyncio.create_task(agent_service.create_turn_async(session_id, request.text))
    
    return SendChatResponse(session_id=session_id)


@app.post("/api/get_chat", response_model=GetChatResponse)
async def get_chat(request: GetChatRequest):
    """
    Get the current status and response from an AI Agent session.
    
    This endpoint retrieves any ongoing output from the AI Agent turn.
    The agent may still be processing, so chat_complete may be False.
    """
    session = session_manager.get_session(request.session_id)
    
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return GetChatResponse(
        response=session.response,
        chat_complete=session.complete
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

