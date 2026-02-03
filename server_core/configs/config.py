# server_core/configs/config.py

import os

class ModelsConfig:
   
    REASONING_MODEL_PATH = os.path.join("models", "llama-3-8b-instruct.Q6_K.gguf")
    REASONING_MODEL_CTX = 4096
    REASONING_MODEL_MAX_TOKENS = 128

    STT_MODEL_PATH = os.path.join("models", "faster-whisper-large-v3")
    SST_BEAM_SIZE = 4
    STT_LANGUAGE = "fa"

    PIPER_PATH = os.path.join("piper", "piper.exe") 
    TSS_MODEL_PATH = os.path.join("models", " fa_IR-amir-medium.onnx")