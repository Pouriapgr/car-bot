# server_core/services/text2speech.py

import asyncio
import subprocess
import logging
from server_core.configs.config import ModelsConfig as MC

logger = logging.getLogger(__name__)

async def text_to_speech(text: str) -> bytes:
    return await asyncio.to_thread(_run_piper_cli, text)

def _run_piper_cli(text):
    try:
        # Command: echo text | piper -m model -f output.wav
        cmd = [
            MC.PIPER_PATH,
            "--model", MC.MODEL_PATH,
            "--output_file", "output.wav"
        ]
        process = subprocess.Popen(
            cmd, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        process.communicate(input=text.encode('utf-8'))
        
        with open("output.wav", "rb") as f:
            data = f.read()
        return data
    
    except Exception as e:
        logger.error(f"CRITICAL TTS PROCESS ERROR: {e}", exc_info=True)
        return b""
