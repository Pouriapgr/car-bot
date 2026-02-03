import io
import asyncio
from faster_whisper import WhisperModel
from server_core.configs.config import ModelsConfig as MC

class Speech2Text:

    def __init__(self, device, compute_type = 'float16'):
        self.model = WhisperModel(MC.STT_MODEL_PATH, device=device, compute_type=compute_type)

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        return await asyncio.to_thread(self._process_transcription, audio_bytes)

    def _process_transcription(self, audio_bytes):
        try:
            audio_file = io.BytesIO(audio_bytes)
            segments, info = self.model.transcribe(audio_file, MC.SST_BEAM_SIZE, language=MC.STT_LANGUAGE)
            
            text = " ".join([segment.text for segment in segments])
            print(f"User said: {text}")
            return text.strip()
        
        except Exception as e:
            print(f"STT Error: {e}")
            return ""
