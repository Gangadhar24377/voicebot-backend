"""
Main FastAPI application for Voicebot Backend.
Interview assistant chatbot for 100x AI Agent Team position.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time

from app.config import settings
from app.utils.logger import app_logger
from app.routes import health, chat, voice


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    app_logger.info("=" * 60)
    app_logger.info("Starting Voicebot Backend")
    app_logger.info(f"Environment: {settings.environment}")
    app_logger.info(f"Debug Mode: {settings.debug}")
    app_logger.info(f"OpenAI Model: {settings.openai_model}")
    app_logger.info(f"CORS Origins: {settings.cors_origins_list}")
    app_logger.info("=" * 60)
    
    yield
    
    # Shutdown
    app_logger.info("Shutting down Voicebot Backend")


# Create FastAPI application
app = FastAPI(
    title="Voicebot Backend API",
    description="AI-powered interview chatbot for Gangadhar K's job application",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and their processing time."""
    start_time = time.time()
    
    # Log request
    app_logger.debug(
        f"Incoming request: {request.method} {request.url.path}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    app_logger.debug(
        f"Completed request: {request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Time: {process_time:.3f}s"
    )
    
    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed error messages."""
    app_logger.warning(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": exc.body
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    app_logger.exception(f"Unexpected error: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


# Include routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(voice.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Voicebot Backend API for 100x Interview",
        "candidate": "Gangadhar K",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "endpoints": {
            "health": "/api/health",
            "chat": "/api/chat",
            "voice_chat": "/api/voice-chat",
            "tts": "/api/tts"
        }
    }


# Additional utility endpoints
@app.get("/ping")
async def ping():
    """Simple ping endpoint for connectivity check."""
    return {"message": "pong"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
