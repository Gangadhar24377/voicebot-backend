"""
Voice endpoints for audio-based conversations.
Handles audio upload, transcription, and TTS response.
"""
import base64
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status, Request
from fastapi.responses import Response
from typing import Optional
from app.models.schemas import VoiceChatResponse, TTSRequest
from app.services.openai_service import openai_service
from app.services.conversation_manager import conversation_manager
from app.services.tts_service import tts_service
from app.config import settings
from app.utils.logger import app_logger, log_request, log_response, log_error

router = APIRouter(prefix="/api", tags=["voice"])


@router.post("/voice-chat", response_model=VoiceChatResponse)
async def voice_chat(
    request: Request,
    audio: UploadFile = File(...),
    session_id: Optional[str] = Form(None)
):
    """
    Voice-based chat endpoint.
    
    Accepts audio file, transcribes it, gets AI response, and converts to speech.
    Creates new session if session_id is not provided.
    """
    log_request("voice_chat", session_id=session_id, filename=audio.filename)
    
    try:
        # Validate file size
        audio_bytes = await audio.read()
        
        if len(audio_bytes) > settings.max_audio_file_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Audio file too large. Max size: {settings.max_audio_file_size_mb}MB"
            )
        
        # Validate file type
        if not audio.filename.lower().endswith(('.wav', '.mp3', '.webm', '.m4a', '.ogg')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported audio format. Supported: WAV, MP3, WebM, M4A, OGG"
            )
        
        app_logger.info(
            f"Processing voice chat: {audio.filename} "
            f"({len(audio_bytes) / 1024:.2f} KB)"
        )
        
        # Transcribe audio
        app_logger.debug("Transcribing audio...")
        transcription = await openai_service.transcribe_audio(audio_bytes, audio.filename)
        app_logger.info(f"Transcription: {transcription}")
        
        # Get or create session
        if not session_id:
            session_id = await conversation_manager.create_session()
            app_logger.info(f"Created new session for voice chat: {session_id}")
        
        # Get conversation history
        messages = await conversation_manager.get_messages(session_id)
        
        if messages is None:
            # Session expired, create new one
            app_logger.warning(f"Session {session_id} not found, creating new session")
            session_id = await conversation_manager.create_session()
            messages = await conversation_manager.get_messages(session_id)
        
        # Add user message
        await conversation_manager.add_message(session_id, "user", transcription)
        
        # Get updated messages
        messages = await conversation_manager.get_messages(session_id)
        
        # Get AI response
        app_logger.debug(f"Getting AI response for session {session_id}")
        response = await openai_service.chat_completion(messages)
        
        # Add assistant response
        await conversation_manager.add_message(session_id, "assistant", response["content"])
        
        # Generate speech from response
        app_logger.debug("Generating speech response...")
        audio_id, audio_bytes = await tts_service.generate_speech(
            response["content"],
            use_cache=False,
            persist=False
        )
        audio_base64 = base64.b64encode(audio_bytes).decode("ascii")
        audio_data_uri = f"data:audio/mpeg;base64,{audio_base64}"
        
        # Create response
        voice_response = VoiceChatResponse(
            transcription=transcription,
            response=response["content"],
            audio_url=None,
            audio_base64=audio_data_uri,
            session_id=session_id
        )
        
        log_response(
            "voice_chat",
            session_id=session_id,
            transcription_length=len(transcription),
            response_length=len(response["content"]),
            audio_id=audio_id
        )
        
        return voice_response
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "voice_chat", "session_id": session_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing voice chat: {str(e)}"
        )


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Text-to-speech endpoint.
    
    Converts text to speech and returns audio file.
    """
    log_request("tts", text_length=len(request.text))
    
    try:
        # Generate speech
        audio_id, audio_bytes = await tts_service.generate_speech(
            request.text,
            request.voice
        )
        
        log_response(
            "tts",
            audio_id=audio_id,
            audio_size=len(audio_bytes)
        )
        
        # Return audio file
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename={audio_id}.mp3"
            }
        )
        
    except Exception as e:
        log_error(e, {"endpoint": "tts", "text_length": len(request.text)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating speech: {str(e)}"
        )


@router.get("/audio/{audio_id}")
async def get_audio(audio_id: str):
    """
    Get audio file by ID.
    
    Returns the MP3 audio file for the given audio_id.
    """
    log_request("get_audio", audio_id=audio_id)
    
    try:
        audio_bytes = await tts_service.get_audio(audio_id)
        
        if audio_bytes is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file {audio_id} not found"
            )
        
        log_response("get_audio", audio_id=audio_id, audio_size=len(audio_bytes))
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"inline; filename={audio_id}.mp3",
                "Cache-Control": "public, max-age=3600"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "get_audio", "audio_id": audio_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving audio: {str(e)}"
        )


@router.delete("/audio/{audio_id}")
async def delete_audio(audio_id: str):
    """
    Delete audio file by ID.
    
    Removes the audio file from storage.
    """
    log_request("delete_audio", audio_id=audio_id)
    
    try:
        deleted = await tts_service.delete_audio(audio_id)
        
        if deleted:
            log_response("delete_audio", audio_id=audio_id, status="deleted")
            return {"message": "Audio file deleted successfully", "audio_id": audio_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file {audio_id} not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "delete_audio", "audio_id": audio_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting audio: {str(e)}"
        )
