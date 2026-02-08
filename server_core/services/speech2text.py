# server_core/services/speech2text.py

import io
import asyncio
import logging
from server_core.configs.config import ModelsConfig as MC
from faster_whisper import WhisperModel

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
            farsi_prompt = "سلام چطوری؟ خوبی؟ دمت گرم. آره بابا حله. خیلی مخلصیم. الان کجایی؟ باشه."
            segments, info = self.model.transcribe(audio_file, 
                                                   beam_size=MC.SST_BEAM_SIZE, 
                                                   language=MC.STT_LANGUAGE, 
                                                   initial_prompt=farsi_prompt, 
                                                   condition_on_previous_text=False,
                                                   patience=1.0,
                                                   temperature=[0.0, 0.2],
                                                   )
            
            text = " ".join([segment.text for segment in segments])
            return text.strip()
        
        except Exception as e:
            logger.error(f"STT TRANSCRIBTION ERROR: {e}", exc_info=True)
            return ""
