# server_core/configs/config.py

import pyaudio
import os

class ModelsConfig:
   
    REASONING_MODEL_PATH = os.path.join("server_core/models", "qwen2.5-7b-instruct-q6_k-00001-of-00002.gguf")
    REASONING_MODEL_CTX = 4096
    REASONING_MODEL_MAX_TOKENS = 128

    STT_MODEL_PATH = os.path.join("server_core/models", "faster-whisper-large-v3")
    SST_BEAM_SIZE = 4
    STT_LANGUAGE = "fa"

    PIPER_PATH = os.path.join("piper", "piper.exe") 
    TSS_MODEL_PATH = os.path.join("server_core/models", " fa_IR-amir-medium.onnx")

class AudioConfig:
    
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    IN_RATE = 16000
    IN_CHUNK = 1280  # openWakeWord expects chunks of 1280 samples
    OUT_RATE = 24000

    WAKE_WORD_THRESHOLD = 0.6
    WAKE_COMMAND = 'alexa'

    VAD_RMS_THRESHOLD = int(os.getenv("VAD_THRESHOLD", 500))
    VAD_SILENCE_CHUNKS_REQUIRED = 12