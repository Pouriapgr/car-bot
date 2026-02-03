import asyncio
from llama_cpp import Llama
from server_core.configs.config import ModelsConfig as MC

class ReasoningModel:
    def __init__(self):
        try:
            self.llm = Llama(model_path=MC.REASONING_MODEL_PATH, n_ctx=MC.REASONING_MODEL_CTX, n_gpu_layers=-1, verbose=False) 
        except Exception as e:
            print(f"CRITICAL LLM ERROR: {e}")
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
        prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{self.SYSTEM_PROMPT}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{self.user_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

        output = self.llm(
            prompt, 
            max_tokens=MC.REASONING_MODEL_MAX_TOKENS, 
            stop=["<|eot_id|>", "\n\n"], 
            echo=False
        )
        
        response_text = output['choices'][0]['text'].strip()
        print(f"Bot thought: {response_text}")

        return {"text": response_text, "should_listen_again": "?" in response_text or "؟" in response_text}
