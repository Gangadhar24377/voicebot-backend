"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for text-based chat."""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What should we know about your life story?",
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class ChatResponse(BaseModel):
    """Response model for text-based chat."""
    response: str = Field(..., description="AI response")
    session_id: str = Field(..., description="Session ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "I'm Gangadhar K, an AI/ML Engineer currently working at SapiensFirst AI...",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2024-11-17T10:30:00Z",
                "tokens_used": 150
            }
        }


class VoiceChatResponse(BaseModel):
    """Response model for voice-based chat."""
    transcription: str = Field(..., description="Transcribed user speech")
    response: str = Field(..., description="AI response text")
    audio_url: Optional[str] = Field(None, description="URL to audio response")
    session_id: str = Field(..., description="Session ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transcription": "What is your number one superpower?",
                "response": "My #1 superpower is taking ideas from concept to working product rapidly...",
                "audio_url": "/api/audio/temp-file-id.mp3",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2024-11-17T10:30:00Z"
            }
        }


class TTSRequest(BaseModel):
    """Request model for text-to-speech conversion."""
    text: str = Field(..., min_length=1, max_length=4096, description="Text to convert to speech")
    voice: Optional[str] = Field(None, description="Voice to use (alloy, echo, fable, onyx, nova, shimmer)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, I'm Gangadhar, an AI/ML Engineer passionate about building agentic AI systems.",
                "voice": "alloy"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    openai_connected: bool = Field(..., description="OpenAI API connectivity status")
    version: str = Field(default="1.0.0", description="API version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-11-17T10:30:00Z",
                "openai_connected": True,
                "version": "1.0.0"
            }
        }


class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid session",
                "detail": "Session expired or does not exist",
                "timestamp": "2024-11-17T10:30:00Z"
            }
        }


class ConversationMessage(BaseModel):
    """Model for a single conversation message."""
    role: str = Field(..., description="Message role (system, user, assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
