# client_edge/audio_service.py

import pyaudio
import numpy as np
import asyncio
from openwakeword.model import Model
from event_bus import EventBus
from states import BotState
from config import AudioConfig as AC


class AudioService:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.bus.subscribe("STATE_CHANGED", self.handle_state)
        self.bus.subscribe("SPEAK_COMMAND", self.play_audio)
        self.state = BotState.SLEEP
        
        self.audio_buffer = [] 
        self.vad_silence_counter = 0
        self.vad_has_spoken = False    

        self.p = pyaudio.PyAudio()
        ### todo: make sure about the mic IN_CHUNK. might need to use buffer extention
        self.input_stream = self.p.open(format=AC.FORMAT, channels=AC.CHANNELS, rate=AC.IN_RATE, input=True, frames_per_buffer=AC.IN_CHUNK)
        self.output_stream = self.p.open(format=AC.FORMAT, channels=AC.CHANNELS, rate=AC.OUT_RATE, output=True)
        self.is_running = True    

        self.oww_model = Model(wakeword_models=[AC.WAKE_COMMAND])
        
        asyncio.create_task(self.audio_loop())

    def _reset_vad_state(self):
        self.audio_buffer.clear()
        self.vad_silence_counter = 0
        self.vad_has_spoken = False

    async def handle_state(self, state):
        previous_state = self.state
        self.state = state
        
        if state == BotState.WAKING_UP:
            await self._play_system_sound("wake_up_ding")
            await self.bus.publish("WAKE_UP_COMPLETE")

        elif state == BotState.GOING_TO_SLEEP:
            await self._play_system_sound("going_to_sleep_sound")
            await self.bus.publish("GOING_TO_SLEEP_COMPLETE")

        elif state == BotState.LISTENING:
            self._reset_vad_state()
            
        elif state in [BotState.IDLE, BotState.SLEEP]:
            self._reset_vad_state()
            self.oww_model.reset()

        elif state in [BotState.THINKING, BotState.SPEAKING, BotState.ACTING]:
            pass

    async def _play_system_sound(self, sound_type):
        print(f"AUDIO: >> Playing sound: {sound_type} <<")

    async def play_audio(self, audio_data: bytes):
        if not audio_data:
            return

        try:
            await asyncio.to_thread(self.output_stream.write, audio_data)
            silence = b'\x00' * 1024
            await asyncio.to_thread(self.output_stream.write, silence)

        except Exception as e:
            print(f"AUDIO ERROR (Playback): {e}")

        finally:
            await self.bus.publish("PLAYBACK_COMPLETE")

    async def audio_loop(self):
        while self.is_running:
            if not self.input_stream.is_active():
                await asyncio.sleep(0.1)
                continue
            try:
                data = await asyncio.to_thread(self.input_stream.read, AC.IN_CHUNK, exception_on_overflow=False)
            except Exception as e:
                print(f"AUDIO READ ERROR: {e}")
                await asyncio.sleep(0.1)
                continue

            audio_np = np.frombuffer(data, dtype=np.int16)

            if self.state in [BotState.SLEEP, BotState.IDLE]:
                prediction = self.oww_model.predict(audio_np)
                if prediction[AC.WAKE_COMMAND] >= AC.WAKE_WORD_THRESHOLD:
                    self.oww_model.reset()
                    await self.bus.publish("WAKE_WORD_RECEIVED")

            elif self.state == BotState.LISTENING:
                rms = np.sqrt(np.mean(audio_np.astype(np.float32)**2))
                is_speech = rms > AC.VAD_RMS_THRESHOLD

                if is_speech:
                    self.vad_silence_counter = 0
                    if not self.vad_has_spoken:
                        self.vad_has_spoken = True

                    self.audio_buffer.append(data) 

                elif self.vad_has_spoken:
                    self.vad_silence_counter += 1
                    self.audio_buffer.append(data)

                    if self.vad_silence_counter >= AC.VAD_SILENCE_CHUNKS_REQUIRED:
                        recorded_audio = b''.join(self.audio_buffer)
                        await self.bus.publish("AUDIO_QUERY_RECEIVED", recorded_audio)
                        self._reset_vad_state() 
                
            elif self.state in [BotState.THINKING, BotState.SPEAKING, BotState.ACTING, BotState.WAKING_UP, BotState.GOING_TO_SLEEP]:
                # We do nothing with the audio data, effectively "muting" the input.
                pass

            await asyncio.sleep(0.01)