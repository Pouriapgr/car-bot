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
    system_manager = BotManager(event_bus)
    gui_service = BotGUI(event_bus, GC.VIDEO_ADDRESS)
    audio_service = BotAudio(event_bus)
    connection_service = DataConnector(event_bus, GC.SERVER_WS_URL)
    idle_timer_service = IdleTimer(event_bus)
    running = True
    logger.info("Event_bus + system_manager + gui_services + audio_service + connection_service + idle_timer_service initiated")
    
    connection_service.run_task()
    logger.info("Client-side socket connection task is running.")
    audio_service.run_task()
    logger.info("Client-side microphone is running.")

    try:
        while running:
            should_continue = await gui_service.render()
            if not should_continue:
                running = False
            await asyncio.sleep(0.04)

    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt detected.")
    except Exception as e:
        logger.error(f"Critical Error in Main Rendering Loop: {e}", exc_info=True)
    finally:
        connection_service.shutdown()
        logger.info("Client-side socket terminated.")
        audio_service.shutdown()
        logger.info("Client-side microphone terminated.")
        gui_service.shutdown()
        logger.info("Client-side display terminated.")
        idle_timer_service.shutdown()
        logger.info("Client-side idle timer terminated.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
