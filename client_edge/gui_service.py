import asyncio
import pygame
import cv2
import numpy as np
import os
from client_edge.event_bus import EventBus

class BotGUI:
    def __init__(self, bus: EventBus, video_folder="assets/videos"):
        self.bus = bus
        self.running = True
        self.video_folder = video_folder
        
        self.video_map = {
            "BOOT": "boot.mp4",
            "IDLE": "idle.mp4",         # e.g., Blinking eyes
            "LISTENING": "listening.mp4", # e.g., Ears perking up
            "THINKING": "thinking.mp4",   # e.g., Spinning gears
            "SPEAKING": "speaking.mp4"    # e.g., Moving mouth
        }
        
        pygame.init()
        self.display_size = (320, 240)
        self.screen = pygame.display.set_mode(self.display_size)
        pygame.display.set_caption("Robot Face")
        self.clock = pygame.time.Clock()

        self.current_state = "BOOT"
        self.cap = None 
        self.current_video_file = None
        
        # Subscribe to events
        self.bus.subscribe("STATE_CHANGED", self.handle_state_change)
        
        self.load_video_for_state("BOOT")

    async def handle_state_change(self, new_state):
        if new_state != self.current_state:
            self.current_state = new_state
            self.load_video_for_state(new_state)

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

    def render_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, self.display_size)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = np.transpose(frame, (1, 0, 2))
                surf = pygame.surfarray.make_surface(frame)
                self.screen.blit(surf, (0, 0))
        else:
            self.screen.fill((0,0,0))
            font = pygame.font.SysFont("Arial", 20)
            text = font.render(self.current_state, True, (255, 255, 255))
            self.screen.blit(text, (10, 10))

        pygame.display.flip()

    async def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.render_frame()
            self.clock.tick(24)
            await asyncio.sleep(0)

        if self.cap:
            self.cap.release()
        pygame.quit()
