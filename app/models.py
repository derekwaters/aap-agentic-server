"""Data models for API requests and responses."""
from pydantic import BaseModel


class SendChatRequest(BaseModel):
    """Request model for send_chat endpoint."""
    text: str


class SendChatResponse(BaseModel):
    """Response model for send_chat endpoint."""
    session_id: str


class GetChatRequest(BaseModel):
    """Request model for get_chat endpoint."""
    session_id: str


class GetChatResponse(BaseModel):
    """Response model for get_chat endpoint."""
    response: str
    chat_complete: bool

