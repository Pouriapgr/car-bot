# client_edge/services/connection_service.py

import aiohttp
import asyncio
import json
import struct
import logging
from client_edge.managers.event_bus import EventBus
from client_edge.configs.config import SocketConfig as SC

logger = logging.getLogger(__name__)

class DataConnector:
    def __init__(self, bus: EventBus, server_ws_url: str):
        self.bus = bus
        self.server_ws_url = server_ws_url 
        self.task = None
        self.ws = None
        self.session = None
        self.is_connected = False

        # Subscribe to outgoing events
        self.bus.subscribe("SERVER_QUERY_INTERACTION", self.send_audio)
        
    def run_task(self):
        self.task = asyncio.create_task(self.maintain_connection())

    async def maintain_connection(self):
        while True:
            try:
                async with aiohttp.ClientSession() as self.session:
                    async with self.session.ws_connect(self.server_ws_url) as ws:
                        self.ws = ws
                        self.is_connected = True
                        
                        await self.bus.publish("NETWORK_CONNECTED") # FUTURE Devlopment

                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                logger.info("Message recieved over web-socket.")
                                await self.handle_server_message(msg.data)
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                logger.info("Error recieved over web-socket." + msg)
                                break
                        self.is_connected = False
                        await self.bus.publish("NETWORK_DISCONNECTED") # FUTURE Devlopment
                        logger.info("Network Disconnected." + msg)

            except Exception as e:
                self.is_connected = False
                logger.error(f"Connection Failed: {e}. Retrying in 3s...")
                await self.bus.publish("NETWORK_DISCONNECTED") # FUTURE Devlopment
                await asyncio.sleep(3) # Wait before retry

    async def handle_server_message(self, message_str):
        try:
            data = json.loads(message_str)
            await self.bus.publish("SERVER_RESPONSE_RECEIVED", data)
            
        except json.JSONDecodeError:
            logger.error(f"Failed to decode server message: {message_str}")
        except Exception as e:
            logger.error(f"Error handling server message: {e}", exc_info=True)


    async def send_audio(self, raw_audio_bytes):
        if not self.is_connected or not self.ws:
            await self.bus.publish("SERVER_ERROR") # FUTURE Devlopment
            logger.info(f"Audio transmition to server error")
            return
        
        wav_data = self._add_wav_header(raw_audio_bytes)
        try:
            await self.ws.send_bytes(wav_data)
        except Exception as e:
            logger.error(f"Failed to send audio to server: {e}", exc_info=True)
            await self.bus.publish("SERVER_ERROR") # FUTURE Devlopment

    def _add_wav_header(self, pcm_data: bytes) -> bytes:
        header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF', 36 + len(pcm_data), b'WAVE', b'fmt ', SC.SAMPLE_WIDTH * 8, 1,
            SC.CHANNELS, SC.RATE,
            SC.RATE * SC.CHANNELS * SC.SAMPLE_WIDTH,
            SC.CHANNELS * SC.SAMPLE_WIDTH,
            16, b'data', len(pcm_data)
        )
        return header + pcm_data


    def shutdown(self):
        self._cancel_task()

    def _cancel_task(self):
        if self.task:
            self.task.cancel()
            self.ws.close()
            self.session.close()
