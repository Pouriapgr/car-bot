# client_edge/event_bus.py

import asyncio
from typing import Callable, Dict, List, Set, Any

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.background_tasks: Set[asyncio.Task] = set()

    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(callback)
        print(f"[BUS]: New subscriber for '{event_name}' - {callback.__name__}")

    def unsubscribe(self, event_name: str, callback: Callable):
        if event_name in self.subscribers:
            try:
                self.subscribers[event_name].remove(callback)
                print(f"[BUS]: Unsubscribed '{callback.__name__}' from '{event_name}'")
            except ValueError:
                pass 

    async def publish(self, event_name: str, data: Any = None):
        if event_name not in self.subscribers:
            return

        # Iterate over a copy [:] to allow safe unsubscribing during loops
        for callback in self.subscribers[event_name][:]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    task = asyncio.create_task(callback(data))
                    self.background_tasks.add(task)
                    task.add_done_callback(self.background_tasks.discard)
                else:
                    callback(data)
            except Exception as e:
                print(f"[BUS ERROR]: {e}")
