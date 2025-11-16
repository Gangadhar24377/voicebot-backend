"""
Health check endpoint for monitoring service status.
"""
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.services.openai_service import openai_service
from app.services.conversation_manager import conversation_manager
from app.services.tts_service import tts_service
from app.utils.logger import app_logger

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns service status and connectivity information.
    """
    app_logger.debug("Health check requested")
    
    # Check OpenAI connectivity
    openai_connected = await openai_service.check_connection()
    
    # Get session statistics
    session_stats = await conversation_manager.get_session_stats()
    
    # Get storage statistics
    storage_stats = await tts_service.get_storage_stats()
    
    status = "healthy" if openai_connected else "degraded"
    
    response = HealthResponse(
        status=status,
        openai_connected=openai_connected
    )
    
    app_logger.info(
        f"Health check: {status} | "
        f"Sessions: {session_stats['active_sessions']} | "
        f"Audio files: {storage_stats.get('total_files', 0)}"
    )
    
    return response


@router.get("/stats")
async def get_stats():
    """
    Get detailed service statistics (for debugging/monitoring).
    """
    session_stats = await conversation_manager.get_session_stats()
    storage_stats = await tts_service.get_storage_stats()
    
    return {
        "sessions": session_stats,
        "storage": storage_stats,
        "openai_connected": await openai_service.check_connection()
    }
