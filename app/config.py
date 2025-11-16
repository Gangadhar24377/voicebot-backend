"""
Configuration management using Pydantic Settings.
All settings are loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_tts_model: str = "tts-1"
    openai_tts_voice: str = "alloy"
    openai_whisper_model: str = "whisper-1"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.7
    openai_timeout_seconds: int = 30
    
    # Application Settings
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Settings
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Conversation Settings
    max_conversation_length: int = 20
    session_timeout_seconds: int = 3600
    max_audio_file_size_mb: int = 25
    
    # Rate Limiting
    max_requests_per_minute: int = 30
    max_requests_per_hour: int = 500
    
    # Personal Context (for system prompt)
    candidate_name: str = "Gangadhar K"
    candidate_email: str = "gangadharkambhamettu@gmail.com"
    candidate_phone: str = "+91 6305470480"
    candidate_linkedin: str = "in/gangadhar-kambhamettu-086a48227"
    candidate_github: str = "github.com/Gangadhar24377"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def max_audio_file_size_bytes(self) -> int:
        """Convert MB to bytes for audio file size limit."""
        return self.max_audio_file_size_mb * 1024 * 1024
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Create cached settings instance.
    This ensures we only load settings once.
    """
    return Settings()


# Global settings instance
settings = get_settings()
