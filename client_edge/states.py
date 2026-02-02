# client_edge/states.py

from enum import Enum

class BotState(Enum):
    WAKING_UP = "WAKING_UP"            # Animation: "I'm waking up"
    IDLE = "IDLE"                      # Active, blinking, waiting for wake word
    GOING_TO_SLEEP = "GOING_TO_SLEEP"  # Animation: "Goodnight"
    SLEEP = "SLEEP"                    # Low power, waiting for wake word
    
    LISTENING = "LISTENING"         # Recording user command
    THINKING = "THINKING"           # Sending to server / Recieving from server
    SPEAKING = "SPEAKING"           # Performing Action = Talking
    ACTING = "ACTING"               # Performing Action = Arbitary Action