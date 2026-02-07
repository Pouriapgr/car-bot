# server_core/server_main.py

import base64
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from server_core.configs.logging_config import setup_logging
from server_core.services.speech2text import Speech2Text
from server_core.services.reasoning import ReasoningModel
from server_core.services import text2speech

setup_logging()
logger = logging.getLogger(__name__)


llm, sst = None, None

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(msg="Server Started...")

    global llm, stt
    llm = ReasoningModel()
    logger.info(msg="LLM initiated correctly.")
    stt = Speech2Text('cuda', 'float16')
    logger.info(msg="STT model initiated correctly.")
    
    yield 

    logger.info(msg="Server terminated.")
        
app = FastAPI(lifespan=lifespan)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    logger.info(msg="Web Socket connection attempt...")
    await websocket.accept()
    logger.info(msg="Web Socket connection succeeded.")

    try:
        while True:
            logger.info(msg="Waiting for audio bytes...")
            audio_bytes = await websocket.receive_bytes()
            logger.info(msg="Audio Recieved.")

            user_text = await stt.transcribe_audio(audio_bytes)
            logger.info(msg="Audio transcribtion done.\n text = " + user_text)
            
            llm_response = await llm.get_response(user_text)
            bot_text = llm_response.get("text", "I am confused.")
            should_listen_again = llm_response.get("should_listen_again", False)
            logger.info(msg="Reasoning done.\n text = " + bot_text + "\nshould_listen_again " + str(should_listen_again))

            audio_out_bytes = await text2speech.text_to_speech(bot_text)
            audio_b64 = base64.b64encode(audio_out_bytes).decode('utf-8')
            logger.info(msg="To speech done.")

            response_payload = {
                "type": "AUDIO_RESPONSE",
                "user_transcription": user_text,
                "bot_text": bot_text,
                "audio_base64": audio_b64,
                "should_listen_again": should_listen_again
            }
            await websocket.send_json(response_payload)
            logger.info(msg="Data sent to the client.")

    except WebSocketDisconnect:
        logger.info("Web socket disconnected.")
    except Exception as e:
        logger.debug(f"Critical Server Error: {e}", exc_info=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
