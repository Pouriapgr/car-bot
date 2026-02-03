# client_edge/configs/config.py

import pyaudio
import os 

from dotenv import load_dotenv
load_dotenv()

# Timer Configuration
class TimerConfig:
    
    TIMER_SECONDS = 60


# Audio Configurations
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

class SocketConfig:

    CHANNELS = 1
    RATE = 16000
    SAMPLE_WIDTH = 2  # Chnages with FORMAT

class GUIConfig:

    DISPLAY_WIDTH = 320
    DISPLAY_HEIGHT = 240
    FRAME_RATE = 24

class GeneralConfig:
    VIDEO_ADDRESS = os.path.join("assets", "videos") 
    SERVER_WS_URL = os.getenv("SERVER_WS_URL", "ws://localhost:8000")