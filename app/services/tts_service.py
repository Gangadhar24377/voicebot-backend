"""
Text-to-Speech service for generating audio responses.
Handles audio caching and cleanup.
"""
import os
import asyncio
from pathlib import Path
from typing import Optional
import hashlib
from datetime import datetime, timedelta
from app.services.openai_service import openai_service
from app.config import settings
from app.utils.logger import app_logger, log_error


class TTSService:
    """Service for text-to-speech operations with caching."""
    
    def __init__(self):
        """Initialize TTS service with temp directory."""
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_old_audio_files())
    
    def _generate_audio_id(self, text: str, voice: str) -> str:
        """
        Generate unique ID for audio file based on text and voice.
        Uses MD5 hash for consistent IDs.
        """
        content = f"{text}:{voice}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_audio_path(self, audio_id: str) -> Path:
        """Get file path for audio ID."""
        return self.temp_dir / f"{audio_id}.mp3"
    
    async def generate_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        use_cache: bool = True
    ) -> tuple[str, bytes]:
        """
        Generate speech from text.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (optional)
            use_cache: Whether to use cached audio if available
        
        Returns:
            Tuple of (audio_id, audio_bytes)
        """
        try:
            voice = voice or settings.openai_tts_voice
            audio_id = self._generate_audio_id(text, voice)
            audio_path = self._get_audio_path(audio_id)
            
            # Check cache
            if use_cache and audio_path.exists():
                app_logger.debug(f"Using cached audio: {audio_id}")
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()
                return audio_id, audio_bytes
            
            # Generate new audio
            app_logger.debug(f"Generating new audio: {audio_id}")
            audio_bytes = await openai_service.text_to_speech(text, voice)
            
            # Save to cache
            with open(audio_path, "wb") as f:
                f.write(audio_bytes)
            
            app_logger.info(
                f"Generated audio {audio_id}: "
                f"{len(text)} chars -> {len(audio_bytes)} bytes"
            )
            
            return audio_id, audio_bytes
            
        except Exception as e:
            log_error(e, {"service": "tts", "text_length": len(text)})
            raise
    
    async def get_audio(self, audio_id: str) -> Optional[bytes]:
        """
        Get audio file by ID.
        
        Args:
            audio_id: Audio file identifier
        
        Returns:
            Audio bytes or None if not found
        """
        audio_path = self._get_audio_path(audio_id)
        
        if not audio_path.exists():
            app_logger.warning(f"Audio file not found: {audio_id}")
            return None
        
        try:
            with open(audio_path, "rb") as f:
                return f.read()
        except Exception as e:
            log_error(e, {"service": "tts", "operation": "get_audio", "audio_id": audio_id})
            return None
    
    async def delete_audio(self, audio_id: str) -> bool:
        """
        Delete audio file.
        
        Args:
            audio_id: Audio file identifier
        
        Returns:
            True if deleted, False if not found
        """
        audio_path = self._get_audio_path(audio_id)
        
        if audio_path.exists():
            try:
                audio_path.unlink()
                app_logger.debug(f"Deleted audio file: {audio_id}")
                return True
            except Exception as e:
                log_error(e, {"service": "tts", "operation": "delete_audio", "audio_id": audio_id})
                return False
        
        return False
    
    async def _cleanup_old_audio_files(self):
        """Background task to cleanup old audio files."""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                cutoff_time = datetime.now() - timedelta(hours=2)
                deleted_count = 0
                
                for audio_file in self.temp_dir.glob("*.mp3"):
                    try:
                        file_time = datetime.fromtimestamp(audio_file.stat().st_mtime)
                        
                        if file_time < cutoff_time:
                            audio_file.unlink()
                            deleted_count += 1
                    except Exception as e:
                        app_logger.error(f"Error deleting old audio file {audio_file}: {e}")
                
                if deleted_count > 0:
                    app_logger.info(f"Cleaned up {deleted_count} old audio files")
                    
            except Exception as e:
                app_logger.error(f"Error in audio cleanup task: {e}")
    
    def get_audio_url(self, audio_id: str, base_url: str = "") -> str:
        """
        Get URL for audio file.
        
        Args:
            audio_id: Audio file identifier
            base_url: Base URL for the API (optional)
        
        Returns:
            Full URL to audio file
        """
        return f"{base_url}/api/audio/{audio_id}"
    
    async def get_storage_stats(self) -> dict:
        """
        Get statistics about audio storage.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            audio_files = list(self.temp_dir.glob("*.mp3"))
            total_size = sum(f.stat().st_size for f in audio_files)
            
            return {
                "total_files": len(audio_files),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "temp_directory": str(self.temp_dir.absolute())
            }
        except Exception as e:
            log_error(e, {"service": "tts", "operation": "get_storage_stats"})
            return {"error": str(e)}


# Global TTS service instance
tts_service = TTSService()
