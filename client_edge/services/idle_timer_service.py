# client_edge/services/idle_timer_service.py

import asyncio
from client_edge.configs.config import TimerConfig
from client_edge.managers.states import BotState

class IdleTimer:
    def __init__(self, bus):
        self.bus = bus
        self.task = None

        self.bus.subscribe("STATE_CHANGED", self.on_state_change)

    async def on_state_change(self, state):
        if self.task:
            self.task.cancel()

        if state == BotState.IDLE:
            self.task = asyncio.create_task(self.countdown())

    async def countdown(self):
        try:
            await asyncio.sleep(TimerConfig.TIMER_SECONDS) 
            await self.bus.publish("IDLE_TIMEOUT")
        except asyncio.CancelledError:
            print("TIMER: Reset")

    def shutdown(self):
        self._cancel_task()

    def _cancel_task(self):
        if self.task:
            self.task.cancel()