# server_core/services/speech2text.py

import io
import asyncio
import logging
from faster_whisper import WhisperModel
from server_core.configs.config import ModelsConfig as MC

logger = logging.getLogger(__name__)

class Speech2Text:

    def __init__(self, device, compute_type = 'float16'):
        try:
            self.model = WhisperModel(MC.STT_MODEL_PATH, device=device, compute_type=compute_type)
        except Exception as e:
            logger.error(f"CRITICAL STT MODEL ERROR: {e}", exc_info=True)
            self.model = None
    
    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        return await asyncio.to_thread(self._process_transcription, audio_bytes)

    def _process_transcription(self, audio_bytes):
        try:
            audio_file = io.BytesIO(audio_bytes)
            segments, info = self.model.transcribe(audio_file, MC.SST_BEAM_SIZE, language=MC.STT_LANGUAGE)
            text = " ".join([segment.text for segment in segments])
            return text.strip()
        
        except Exception as e:
            logger.error(f"STT TRANSCRIBTION ERROR: {e}", exc_info=True)
            return ""
