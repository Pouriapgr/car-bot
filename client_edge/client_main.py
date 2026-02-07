# client_edge/main.py

import logging
import asyncio
from client_edge.managers.event_bus import EventBus
from client_edge.managers.manager import BotManager
from client_edge.services.gui_service import BotGUI
from client_edge.services.audio_service import BotAudio
from client_edge.services.connection_service import DataConnector
from client_edge.services.idle_timer_service import IdleTimer
from client_edge.configs.config import GeneralConfig as GC
from client_edge.configs.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

async def main():
   
    event_bus = EventBus()
    logger.info("Event Bus initiated")
    system_manager = BotManager(event_bus)
    gui_service = BotGUI(event_bus, GC.VIDEO_ADDRESS)
    audio_service = BotAudio(event_bus)
    connection_service = DataConnector(event_bus, GC.SERVER_WS_URL)
    idle_timer_service = IdleTimer(event_bus)
    running = True
    
    connection_service.run_task()
    audio_service.run_task()

    try:
        while running:
            should_continue = await gui_service.render()
            if not should_continue:
                running = False
            await asyncio.sleep(0.04)

    except KeyboardInterrupt:
        print("Keyboard Interrupt detected.")
    except Exception as e:
        print(f"Critical Error in Main Loop: {e}", exc_info=True)
    finally:
        connection_service.shutdown()
        audio_service.shutdown()
        gui_service.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
