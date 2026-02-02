import aiohttp
import asyncio
import json
import struct
import logging
from client_edge.event_bus import EventBus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataConnector")

class DataConnector:
    def __init__(self, bus: EventBus, server_ws_url: str):
        self.bus = bus
        self.server_ws_url = server_ws_url 
        self.ws = None
        self.session = None
        self.is_connected = False
        
        # Subscribe to outgoing events
        self.bus.subscribe("SERVER_QUERY_INTERACTION", self.send_audio)
        
        asyncio.create_task(self.maintain_connection())

    async def maintain_connection(self):
        while True:
            try:
                logger.info(f"Connecting to {self.server_ws_url}...")
                
                async with aiohttp.ClientSession() as self.session:
                    async with self.session.ws_connect(self.server_ws_url) as ws:
                        self.ws = ws
                        self.is_connected = True
                        logger.info("WebSocket Connected!")
                        
                        await self.bus.publish("NETWORK_CONNECTED") # FUTURE Devlopment

                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self.handle_server_message(msg.data)
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                logger.error(f"WebSocket Error: {ws.exception()}")
                                break
                        self.is_connected = False
                        logger.warning("WebSocket Connection Closed")
                        await self.bus.publish("NETWORK_DISCONNECTED") # FUTURE Devlopment

            except Exception as e:
                self.is_connected = False
                logger.error(f"Connection Failed: {e}. Retrying in 3s...")
                await self.bus.publish("NETWORK_DISCONNECTED") # FUTURE Devlopment
                await asyncio.sleep(3) # Wait before retry

    async def handle_server_message(self, message_str):
        try:
            data = json.loads(message_str)
            logger.info("Received Server Response")
            await self.bus.publish("SERVER_RESPONSE_RECEIVED", data)
            
        except json.JSONDecodeError:
            logger.error(f"Failed to decode server message: {message_str}")
        except Exception as e:
            logger.error(f"Error handling server message: {e}")

    async def send_audio(self, raw_audio_bytes):
        if not self.is_connected or not self.ws:
            logger.error("Cannot send audio: WebSocket not connected")
            await self.bus.publish("SERVER_ERROR") # FUTURE Devlopment
            return

        logger.info(f"Uploading {len(raw_audio_bytes)} bytes via WebSocket...")
        
        wav_data = self._add_wav_header(raw_audio_bytes)
        try:
            await self.ws.send_bytes(wav_data)
        except Exception as e:
            logger.error(f"Failed to send audio: {e}")
            await self.bus.publish("SERVER_ERROR") # FUTURE Devlopment

    def _add_wav_header(self, pcm_data: bytes) -> bytes:
        header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF', 36 + len(pcm_data), b'WAVE', b'fmt ', 16, 1,
            self.CHANNELS, self.RATE,
            self.RATE * self.CHANNELS * self.SAMPLE_WIDTH,
            self.CHANNELS * self.SAMPLE_WIDTH,
            16, b'data', len(pcm_data)
        )
        return header + pcm_data
