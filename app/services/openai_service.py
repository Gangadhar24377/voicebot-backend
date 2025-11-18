"""
Service for interacting with OpenAI API.
Handles chat completions, transcriptions, and text-to-speech.
"""
import asyncio
from typing import List, Dict, Optional, AsyncIterator
from openai import AsyncOpenAI, OpenAIError
from app.config import settings
from app.utils.logger import app_logger, log_openai_call, log_error


class OpenAIService:
    """Service class for OpenAI API operations."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout_seconds
        )
        self.model = settings.openai_model
        self.tts_model = settings.openai_tts_model
        self.tts_voice = settings.openai_tts_voice
        self.whisper_model = settings.openai_whisper_model
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Create a chat completion using OpenAI API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Dictionary with response text and metadata
        
        Raises:
            OpenAIError: If API call fails
        """
        try:
            app_logger.debug(f"Creating chat completion with {len(messages)} messages")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or settings.openai_temperature,
                max_tokens=max_tokens or settings.openai_max_tokens
            )
            
            result = {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }
            
            log_openai_call(
                model=self.model,
                tokens_used=result["tokens_used"],
                finish_reason=result["finish_reason"]
            )
            
            return result
            
        except OpenAIError as e:
            log_error(e, {"service": "openai", "operation": "chat_completion"})
            raise
        except Exception as e:
            log_error(e, {"service": "openai", "operation": "chat_completion"})
            raise
    
    async def transcribe_audio(self, audio_file: bytes, filename: str = "audio.wav") -> str:
        """
        Transcribe audio to text using Whisper API.
        
        Args:
            audio_file: Audio file bytes
            filename: Original filename (for format detection)
        
        Returns:
            Transcribed text
        
        Raises:
            OpenAIError: If transcription fails
        """
        try:
            app_logger.debug(f"Transcribing audio file: {filename}")
            
            # Create a file-like object from bytes
            from io import BytesIO
            audio_buffer = BytesIO(audio_file)
            audio_buffer.name = filename
            
            response = await self.client.audio.transcriptions.create(
                model=self.whisper_model,
                file=audio_buffer
            )
            
            transcribed_text = response.text
            
            log_openai_call(
                model=self.whisper_model,
                operation="transcription",
                text_length=len(transcribed_text)
            )
            
            return transcribed_text
            
        except OpenAIError as e:
            log_error(e, {"service": "openai", "operation": "transcribe_audio"})
            raise
        except Exception as e:
            log_error(e, {"service": "openai", "operation": "transcribe_audio"})
            raise
    
    async def text_to_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.25  # Faster speed for quicker response
    ) -> bytes:
        """
        Convert text to speech using OpenAI TTS API.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speech speed (0.25 to 4.0, default 1.25 for faster response)
        
        Returns:
            Audio file bytes (MP3 format)
        
        Raises:
            OpenAIError: If TTS fails
        """
        try:
            app_logger.debug(f"Converting text to speech: {text[:50]}...")
            
            response = await self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice or self.tts_voice,
                input=text,
                speed=speed
            )
            
            # Get audio content - use .content instead of iter_bytes() for Python 3.13
            audio_content = response.content
            
            log_openai_call(
                model=self.tts_model,
                operation="text_to_speech",
                text_length=len(text),
                audio_size=len(audio_content)
            )
            
            return audio_content
            
        except OpenAIError as e:
            log_error(e, {"service": "openai", "operation": "text_to_speech"})
            raise
        except Exception as e:
            log_error(e, {"service": "openai", "operation": "text_to_speech"})
            raise
    
    async def check_connection(self) -> bool:
        """
        Check if OpenAI API is accessible.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Make a minimal API call to check connectivity
            await self.client.models.list()
            return True
        except Exception as e:
            log_error(e, {"service": "openai", "operation": "check_connection"})
            return False
    
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncIterator[str]:
        """
        Stream chat completion responses (for future use).
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Yields:
            Chunks of response text
        """
        try:
            app_logger.debug(f"Streaming chat completion with {len(messages)} messages")
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or settings.openai_temperature,
                max_tokens=max_tokens or settings.openai_max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except OpenAIError as e:
            log_error(e, {"service": "openai", "operation": "stream_chat_completion"})
            raise
        except Exception as e:
            log_error(e, {"service": "openai", "operation": "stream_chat_completion"})
            raise


# Global OpenAI service instance
openai_service = OpenAIService()
