import asyncio
from llama_cpp import Llama

MODEL_PATH = "models/llama-3-8b-instruct.Q6_K.gguf"

try:
    llm = Llama(model_path=MODEL_PATH, n_ctx=4096, n_gpu_layers=-1, verbose=False) 
except Exception as e:
    print(f"CRITICAL LLM ERROR: {e}")
    llm = None

SYSTEM_PROMPT = """
                You are a helpful robot assistant. 
                Your responses are spoken aloud, so keep them concise (1-2 sentences). 
                Be witty and friendly. Do not use markdown or emojis.
                """

async def get_response(user_text: str) -> dict:
    if not llm:
        return {"text": "My brain is offline.", "should_listen_again": False}
    return await asyncio.to_thread(_generate, user_text)

def _generate(user_text):
    prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{SYSTEM_PROMPT}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{user_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

    output = llm(
        prompt, 
        max_tokens=128, 
        stop=["<|eot_id|>", "\n\n"], 
        echo=False
    )
    
    response_text = output['choices'][0]['text'].strip()
    print(f"Bot thought: {response_text}")

    return {
        "text": response_text,
        "should_listen_again": "?" in response_text
    }
