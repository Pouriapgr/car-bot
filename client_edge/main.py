import asyncio
import pygame
from configs.config import Config
from managers.event_bus import EventBus
from client_edge.managers.manager import SystemManager
from client_edge.services.gui_service import GuiService
from services.audio_service import AudioService
from services.connection_service import ConnectionService

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ClientRunner")

async def main():
    # 1. Hardware & Pygame Setup
    # --------------------------
    pygame.init()
    
    # Set resolution based on Config or default to Pi display (e.g., 480x320)
    screen_width = getattr(Config, 'SCREEN_WIDTH', 800)
    screen_height = getattr(Config, 'SCREEN_HEIGHT', 480)
    
    # Initialize Screen
    # FULLSCREEN is recommended for the car display
    screen = pygame.display.set_mode((screen_width, screen_height)) 
    pygame.display.set_caption("Car Bot Assistant")
    pygame.mouse.set_visible(False) # Hide cursor for production feel

    clock = pygame.time.Clock()

    # 2. Initialize Core Components
    # -----------------------------
    event_bus = EventBus()

    # The SystemManager handles State logic (Idle -> Listening -> Speaking)
    system_manager = SystemManager(event_bus)

    # Services
    gui_service = GuiService(event_bus, screen)
    audio_service = AudioService(event_bus)
    connection_service = ConnectionService(event_bus)

    # 3. Start Background Tasks
    # -------------------------
    # Create tasks for services that run continuously (Network, Audio Listening)
    
    # Start the WebSocket connection loop
    network_task = asyncio.create_task(connection_service.maintain_connection())
    
    # Start the Audio Input loop (VAD / Recording)
    # audio_service.start() usually sets up the PyAudio streams
    await audio_service.start() 

    logger.info("Car Bot Client Initialized. Starting Main Loop...")

    running = True

    try:
        # 4. Main Execution Loop
        # ----------------------
        while running:
            
            # --- A. Pygame Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # --- B. Update GUI (Face Animation) ---
            # This calls the async wrapper that runs OpenCV in the executor
            await gui_service.update_frame()
            
            # Flip the display (Render to screen) - Must happen on Main Thread
            pygame.display.flip()

            # --- C. System Logic Tick ---
            # Give the asyncio event loop time to process network packets
            # and audio chunks. 0.01s = 10ms sleep.
            # This limits the GUI to approx 100 FPS max, leaving CPU for logic.
            await asyncio.sleep(0.01)

    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt detected.")
    except Exception as e:
        logger.error(f"Critical Error in Main Loop: {e}", exc_info=True)
    finally:
        # 5. Cleanup
        # ----------
        logger.info("Shutting down...")
        network_task.cancel()
        audio_service.shutdown() # Ensure PyAudio streams are closed
        pygame.quit()
        logger.info("Cleanup complete. Goodbye.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
