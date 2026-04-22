"""
Voice Service — Browser TTS Edition
=====================================
AWS Polly has been replaced with the browser's built-in Web Speech API.
This service now simply returns the text to the frontend, which synthesizes
the voice locally using the SpeechSynthesis API (zero latency, zero cost).
"""
import logging

logger = logging.getLogger(__name__)


class VoiceService:
    def __init__(self):
        """No external dependencies needed — TTS is handled by the browser."""
        pass

    def synthesize_speech(self, text, voice_id='Matthew', engine='neural'):
        """
        Polly has been removed. The frontend handles voice synthesis via
        the Web Speech API (window.speechSynthesis). This method is kept
        for interface compatibility but returns None for the audio_url.
        The recruiter_response_text field in the API response is what
        the frontend reads aloud.
        """
        logger.debug("Voice synthesis skipped — delegated to browser Web Speech API.")
        return None

    def get_audio_url(self, s3_key):
        """No audio URLs needed — browser handles TTS locally."""
        return None
