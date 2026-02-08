# server_core/testers/speech2text_tester.py

import asyncio
import pyaudio
import numpy as np
import logging
import wave
import io
from server_core.services.speech2text import Speech2Text
from server_core.configs.config import AudioConfig as AC

def create_wav_bytes(pcm_data: bytes) -> bytes:
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wav_file:
        wav_file.setnchannels(AC.CHANNELS)
        wav_file.setsampwidth(2)
        wav_file.setframerate(AC.IN_RATE)
        wav_file.writeframes(pcm_data)
    
    wav_io.seek(0)
    return wav_io.read()

async def run_tester():
    
    stt = Speech2Text(device='cuda', compute_type='float16')
    p = pyaudio.PyAudio()
    
    try:
        input_stream = p.open(
            format=AC.FORMAT,
            channels=AC.CHANNELS,
            rate=AC.IN_RATE,
            input=True,
            frames_per_buffer=AC.CHUNK
        )
    except Exception as e:
        print(f"Failed to open microphone: {e}")
        return

    print("Microphone Active. Speak now... (Press Ctrl+C to stop)")

    audio_buffer = []
    vad_silence_counter = 0
    vad_has_spoken = False
    is_running = True

    try:
        while is_running:
            if input_stream.get_read_available() < AC.IN_CHUNK:
                await asyncio.sleep(0.01)
                continue
            
            data = input_stream.read(AC.IN_CHUNK, exception_on_overflow=False)
            
            audio_np = np.frombuffer(data, dtype=np.int16)
            
            rms = np.sqrt(np.mean(audio_np.astype(np.float32)**2))
            is_speech = rms > AC.VAD_RMS_THRESHOLD

            if is_speech:
                vad_silence_counter = 0
                if not vad_has_spoken:
                    print(">> Speech started...")
                    vad_has_spoken = True
                
                audio_buffer.append(data)

            elif vad_has_spoken:
                vad_silence_counter += 1
                audio_buffer.append(data)

                if vad_silence_counter >= AC.VAD_SILENCE_CHUNKS:
                    print("<< End of sentence detected. Processing...")
                    
                    raw_audio = b''.join(audio_buffer)
                    wav_audio = create_wav_bytes(raw_audio)

                    print.info("Transcribing...")
                    text = await stt.transcribe_audio(wav_audio)
                    
                    print("\n" + "="*40)
                    print(f"TRANSCRIPTION: {text}")
                    print("="*40 + "\n")

                    audio_buffer = []
                    vad_silence_counter = 0
                    vad_has_spoken = False
                    print("Ready for next phrase...")
            
            await asyncio.sleep(0.001)

    except KeyboardInterrupt:
        print("Stopping tester...")
    finally:
        input_stream.stop_stream()
        input_stream.close()
        p.terminate()

if __name__ == "__main__":
    try:
        asyncio.run(run_tester())
    except KeyboardInterrupt:
        pass