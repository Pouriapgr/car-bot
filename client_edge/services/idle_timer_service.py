# client_edge/services/idle_timer_service.py

import logging
import asyncio
from client_edge.configs.config import TimerConfig as TC
from client_edge.managers.states import BotState

logger = logging.getLogger(__name__)

class IdleTimer:
    def __init__(self, bus):
        self.bus = bus
        self.task = None

        self.bus.subscribe("STATE_CHANGED", self.on_state_change)

    async def on_state_change(self, state):
        self._cancel_task()

        if state == BotState.IDLE:
            self.task = asyncio.create_task(self.countdown())

    async def countdown(self):
        try:
            logger.info(f"Idle timer started for {TC.TIMER_SECONDS} seconds.")
            await asyncio.sleep(TC.TIMER_SECONDS) 
            await self.bus.publish("IDLE_TIMEOUT")
            logger.info(f"Idle Timeout initiated.")
        except asyncio.CancelledError:
            logger.info(f"Idle timer reset.")

    def shutdown(self):
        self._cancel_task()

    def _cancel_task(self):
        if self.task:
            self.task.cancel()