import asyncio
import pygame
from managers.event_bus import EventBus
from client_edge.managers.manager import BotManager
from client_edge.services.gui_service import BotGUI
from client_edge.services.audio_service import BotAudio
from client_edge.services.connection_service import DataConnector
from client_edge.configs.config import GeneralConfig as GC


async def main():
   
    event_bus = EventBus()
    system_manager = BotManager(event_bus)
    gui_service = BotGUI(event_bus, GC.VIDEO_ADDRESS)
    audio_service = BotAudio(event_bus)
    connection_service = DataConnector(event_bus, GC.SERVER_WS_URL)

    running = True

    try:
        while running:
            pass

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
