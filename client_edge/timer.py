import asyncio
from config import TimerConfig
from states import BotState

class IdleTimer:
    def __init__(self, bus):
        self.bus = bus
        self.timer_task = None

    async def on_state_change(self, state):
        if self.timer_task:
            self.timer_task.cancel()

        if state == BotState.IDLE:
            self.timer_task = asyncio.create_task(self.countdown())

    async def countdown(self):
        try:
            await asyncio.sleep(TimerConfig.TIMER_COUNTER) 
            await self.bus.publish("IDLE_TIMEOUT")
        except asyncio.CancelledError:
            print("TIMER: Reset")