"""
Chat endpoints for text-based conversations.
"""
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.services.openai_service import openai_service
from app.services.conversation_manager import conversation_manager
from app.utils.logger import app_logger, log_request, log_response, log_error

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Text-based chat endpoint.
    
    Accepts a user message and returns AI response with conversation context.
    Creates new session if session_id is not provided.
    """
    log_request("chat", session_id=request.session_id, message_length=len(request.message))
    
    try:
        # Get or create session
        session_id = request.session_id
        
        if not session_id:
            session_id = await conversation_manager.create_session()
            app_logger.info(f"Created new session for chat: {session_id}")
        
        # Get conversation history
        messages = await conversation_manager.get_messages(session_id)
        
        if messages is None:
            # Session expired or doesn't exist, create new one
            app_logger.warning(f"Session {session_id} not found, creating new session")
            session_id = await conversation_manager.create_session()
            messages = await conversation_manager.get_messages(session_id)
        
        # Add user message to history
        await conversation_manager.add_message(session_id, "user", request.message)
        
        # Get updated messages including user message
        messages = await conversation_manager.get_messages(session_id)
        
        # Get AI response
        app_logger.debug(f"Getting AI response for session {session_id}")
        response = await openai_service.chat_completion(messages)
        
        # Add assistant response to history
        await conversation_manager.add_message(session_id, "assistant", response["content"])
        
        # Create response
        chat_response = ChatResponse(
            response=response["content"],
            session_id=session_id,
            tokens_used=response["tokens_used"]
        )
        
        log_response(
            "chat",
            session_id=session_id,
            tokens_used=response["tokens_used"],
            response_length=len(response["content"])
        )
        
        return chat_response
        
    except Exception as e:
        log_error(e, {"endpoint": "chat", "session_id": request.session_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a conversation session.
    
    Removes all conversation history for the given session.
    """
    log_request("delete_session", session_id=session_id)
    
    try:
        deleted = await conversation_manager.delete_session(session_id)
        
        if deleted:
            log_response("delete_session", session_id=session_id, status="deleted")
            return {"message": "Session deleted successfully", "session_id": session_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "delete_session", "session_id": session_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting session: {str(e)}"
        )


@router.get("/session/{session_id}/messages")
async def get_session_messages(session_id: str):
    """
    Get all messages for a session.
    
    Returns the conversation history excluding the system prompt.
    """
    log_request("get_messages", session_id=session_id)
    
    try:
        messages = await conversation_manager.get_messages(session_id)
        
        if messages is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Exclude system message for user display
        user_messages = [msg for msg in messages if msg["role"] != "system"]
        
        log_response("get_messages", session_id=session_id, message_count=len(user_messages))
        
        return {
            "session_id": session_id,
            "message_count": len(user_messages),
            "messages": user_messages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "get_messages", "session_id": session_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving messages: {str(e)}"
        )
