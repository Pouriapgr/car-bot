# client_edge/manager.py

from client_edge.managers.event_bus import EventBus
from client_edge.managers.states import BotState

class BotManager:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.state = BotState.SLEEP
        self.next_state_after_action = BotState.IDLE 

        # SUBSCRIBE TO INPUTS
        self.bus.subscribe("WAKE_WORD_RECEIVED"      , self.on_wake_word_received      )
        self.bus.subscribe("AUDIO_QUERY_RECEIVED"    , self.on_audio_query_received    )
        self.bus.subscribe("SERVER_RESPONSE_RECEIVED", self.on_server_response_received)

        self.bus.subscribe("WAKE_UP_COMPLETE"        , self.on_wake_up_complete        )
        self.bus.subscribe("PLAYBACK_DONE"           , self.on_playback_complete       )
        self.bus.subscribe("ACTION_COMPLETE"         , self.on_action_complete         )

        self.bus.subscribe("IDLE_TIMEOUT"            , self.on_idle_timeout            )

    # --- THE CENTRAL TRANSITION FUNCTION ---
    async def set_state(self, new_state):
        if self.state == new_state: return
        self.state = new_state
        await self.bus.publish("STATE_CHANGED", self.state)


    # --- EVENT HANDLERS ---
    
    async def on_wake_word_received(self, _):
        if self.state == BotState.SLEEP:
            await self.set_state(BotState.WAKING_UP)
        elif self.state == BotState.IDLE:
            await self.set_state(BotState.LISTENING)
        
    async def on_audio_query_received(self, data):
        if self.state == BotState.LISTENING:
            await self.set_state(BotState.THINKING)
            await self.bus.publish("SERVER_QUERY_INTERACTION", data=data)

    async def on_server_response_received(self, data):
        if self.state == BotState.THINKING:
            if data.get('should_listen_again'):
                self.next_state_after_action = BotState.LISTENING
            else:
                self.next_state_after_action = BotState.IDLE

            await self.set_state(BotState.SPEAKING)
            await self.bus.publish("SPEAK_COMMAND", data.get('audio_bytes'))


    async def on_wake_up_complete(self, _):
        if self.state == BotState.WAKING_UP:
            await self.set_state(BotState.LISTENING)
            
    async def on_playback_complete(self, _):
        if self.state == BotState.SPEAKING:
            await self.set_state(self.next_state_after_action)
            self.next_state_after_action = BotState.IDLE
            
    async def on_action_complete(self, _):
        if self.state == BotState.SPEAKING:
            await self.set_state(self.next_state_after_action)
            self.next_state_after_action = BotState.IDLE


    async def on_idle_timeout(self, _):
        if self.state == BotState.IDLE:
            await self.set_state(BotState.GOING_TO_SLEEP)
            await self.set_state(BotState.SLEEP)
