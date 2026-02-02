import pyaudio

# Timer Configuration
class TimerConfig:
    
    TIMER_COUNTER = 60


# Audio Configurations
class AudioConfig:
    
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    IN_RATE = 16000
    IN_CHUNK = 1280  # openWakeWord expects chunks of 1280 samples
    OUT_RATE = 24000

    WAKE_WORD_THRESHOLD = 0.6
    WAKE_COMMAND = 'alexa'
    
    VAD_RMS_THRESHOLD = 500
    VAD_SILENCE_CHUNKS_REQUIRED = 12