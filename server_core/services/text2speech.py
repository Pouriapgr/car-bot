import asyncio
import wave
import os
import subprocess

PIPER_PATH = "./piper/piper.exe" 
MODEL_PATH = "models/en_US-lessac-high.onnx"

async def text_to_speech(text: str) -> bytes:
    return await asyncio.to_thread(_run_piper_cli, text)

def _run_piper_cli(text):
    try:
        # Command: echo text | piper -m model -f output.wav
        cmd = [
            PIPER_PATH,
            "--model", MODEL_PATH,
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
        print(f"Piper Error: {e}")
        return b""
