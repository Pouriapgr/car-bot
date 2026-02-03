import base64
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from server_core.services.speech2text import Speech2Text
from server_core.services.reasoning import ReasoningModel
from server_core.services import text2speech

llm = None
stt = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    
    global llm, stt
    llm = ReasoningModel()
    stt = Speech2Text('cuda', 'float16')
    
    yield 

    print("Server Terminated")
        
app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            audio_bytes = await websocket.receive_bytes()
            
            user_text = await stt.transcribe_audio(audio_bytes)
            
            if not user_text:
                print("No speech detected.")
                continue

            llm_response = await llm.get_response(user_text)
            bot_text = llm_response.get("text", "I am confused.")
            should_listen_again = llm_response.get("should_listen_again", False)

            audio_out_bytes = await text2speech.text_to_speech(bot_text)
            
            audio_b64 = base64.b64encode(audio_out_bytes).decode('utf-8')

            response_payload = {
                "type": "AUDIO_RESPONSE",
                "user_transcription": user_text,
                "bot_text": bot_text,
                "audio_base64": audio_b64,
                "should_listen_again": should_listen_again
            }

            await websocket.send_json(response_payload)

    except WebSocketDisconnect:
        print("Client Disconnected")
    except Exception as e:
        ptin(f"Critical Server Error: {e}", exc_info=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
