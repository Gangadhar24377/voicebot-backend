"""
Logging configuration using loguru.
Provides structured logging for the application.
"""
import sys
from loguru import logger
from app.config import settings


def setup_logger():
    """
    Configure logger with appropriate settings.
    Removes default handler and adds custom configuration.
    """
    # Remove default handler
    logger.remove()
    
    # Add custom handler with format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Console logging
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # File logging (if in production)
    if settings.is_production:
        logger.add(
            "logs/app_{time:YYYY-MM-DD}.log",
            rotation="00:00",  # New file at midnight
            retention="30 days",  # Keep logs for 30 days
            compression="zip",  # Compress old logs
            format=log_format,
            level=settings.log_level,
            backtrace=True,
            diagnose=False  # Don't include sensitive info in production logs
        )
    
    return logger


# Initialize logger
app_logger = setup_logger()


def log_request(endpoint: str, session_id: str = None, **kwargs):
    """Log incoming request with context."""
    context = {"endpoint": endpoint, "session_id": session_id}
    context.update(kwargs)
    app_logger.info(f"Request received", extra=context)


def log_response(endpoint: str, session_id: str = None, status: str = "success", **kwargs):
    """Log outgoing response with context."""
    context = {"endpoint": endpoint, "session_id": session_id, "status": status}
    context.update(kwargs)
    app_logger.info(f"Response sent", extra=context)


def log_error(error: Exception, context: dict = None):
    """Log error with full context and traceback."""
    error_context = {"error_type": type(error).__name__, "error_message": str(error)}
    if context:
        error_context.update(context)
    app_logger.exception(f"Error occurred: {str(error)}", extra=error_context)


def log_openai_call(model: str, tokens_used: int = None, **kwargs):
    """Log OpenAI API call for monitoring."""
    context = {"model": model, "tokens_used": tokens_used}
    context.update(kwargs)
    app_logger.debug(f"OpenAI API call", extra=context)
