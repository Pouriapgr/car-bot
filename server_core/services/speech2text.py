import io
import asyncio
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cuda", compute_type="float16")

async def transcribe_audio(audio_bytes: bytes) -> str:
    return await asyncio.to_thread(_process_transcription, audio_bytes)

def _process_transcription(audio_bytes):
    try:
        audio_file = io.BytesIO(audio_bytes)
        segments, info = model.transcribe(audio_file, beam_size=3, language="en")
        
        text = " ".join([segment.text for segment in segments])
        print(f"User said: {text}")
        return text.strip()
    
    except Exception as e:
        print(f"STT Error: {e}")
        return ""
