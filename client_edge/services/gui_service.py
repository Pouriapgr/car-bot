# client_edge/services/gui_service.py

import asyncio
import pygame
import cv2
import numpy as np
import os
from client_edge.managers.event_bus import EventBus
from client_edge.configs.config import GUIConfig as GC

class BotGUI:
    def __init__(self, bus: EventBus, video_folder="assets/videos"):
        self.bus = bus
        self.running = True
        self.video_folder = video_folder
        
        self.video_map = {
            "BOOT": "boot.mp4",
            "WAKING_UP": "waking_up.mp4",
            "GOING_TO_SLEEP": "going_to_sleep.mp4",
            "SLEEP": "sleep.mp4",
            "IDLE": "idle.mp4",            # e.g., Blinking eyes
            "LISTENING": "listening.mp4",  # e.g., Ears perking up
            "THINKING": "thinking.mp4",    # e.g., Spinning gears
            "SPEAKING": "speaking.mp4",    # e.g., Moving mouth
            "ACTING": "acting.mp4"
        }
        
        pygame.init()
        self.display_size = (GC.DISPLAY_WIDTH, GC.DISPLAY_HEIGHT)
        self.screen = pygame.display.set_mode(self.display_size)
        pygame.display.set_caption("Robot Face")
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()

        self.current_state = "BOOT"
        self.cap = None 
        self.current_video_file = None
        self.loop = asyncio.get_running_loop()
        
        # Subscribe to events
        self.bus.subscribe("STATE_CHANGED", self.handle_state_change)
        
        self.load_video_for_state("BOOT")

    async def handle_state_change(self, new_state):
        if new_state != self.current_state:
            self.current_state = new_state
            self.load_video_for_state(new_state.name)

    def load_video_for_state(self, state):
        filename = self.video_map.get(state, "idle.mp4")
        filepath = os.path.join(self.video_folder, filename)
        
        if not os.path.exists(filepath):
            print(f"Video file not found: {filepath}")
            return

        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(filepath)
        self.current_video_file = filename

    def _process_frame_job(self):
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret: return None

        frame = cv2.resize(frame, self.display_size)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.transpose(frame, (1, 0, 2))
        return frame


    async def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
        try:
            frame_data = await self.loop.run_in_executor(None, self._process_frame_job)
            if frame_data is not None:
                surf = pygame.surfarray.make_surface(frame_data)
                self.screen.blit(surf, (0, 0))
            else:
                self.screen.fill((0,0,0))
        except Exception as e:
            print(f"GUI Error: {e}")

        pygame.display.flip()
        
        return True

    
    def shutdown(self):
        if self.cap:
            self.cap.release()
        pygame.quit()
        self._cancel_task()

    def _cancel_task(self):
        pass
 #      self.task.cancel()
        
        