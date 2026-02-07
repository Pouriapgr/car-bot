# server_core/services/reasoning.py

import asyncio
import logging
from llama_cpp import Llama
from server_core.configs.config import ModelsConfig as MC

logger = logging.getLogger(__name__)

class ReasoningModel:
    def __init__(self):
        try:
            self.llm = Llama(model_path=MC.REASONING_MODEL_PATH, n_ctx=MC.REASONING_MODEL_CTX, n_gpu_layers=-1, verbose=False) 
        except Exception as e:
            logger.error(f"CRITICAL LLM ERROR: {e}", exc_info=True)
            self.llm = None

        self.SYSTEM_PROMPT = """
                        You are a helpful robot assistant. 
                        Your responses are spoken aloud, so keep them concise (1-2 sentences). 
                        Be witty and friendly. Do not use markdown or emojis.
                        """

    async def get_response(self, user_text: str) -> dict:
        if not self.llm:
            return {"text": "My brain is offline.", "should_listen_again": False}
        return await asyncio.to_thread(self._generate, user_text)

    def _generate(self, user_text):
        prompt = (
            f"<|im_start|>system\n{self.SYSTEM_PROMPT}<|im_end|>\n"
            f"<|im_start|>user\n{user_text}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        output = self.llm(
            prompt, 
            max_tokens=MC.REASONING_MODEL_MAX_TOKENS, 
            stop=["<|eot_id|>", "\n\n"], 
            echo=False
        )
        
        response_text = output['choices'][0]['text'].strip()
        return {"text": response_text, "should_listen_again": "?" in response_text or "؟" in response_text}
