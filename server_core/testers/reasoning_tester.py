# server_core/testers/reasoning_tester.py

import asyncio
from server_core.services.reasoning import ReasoningModel

async def test():

    llm = ReasoningModel()

    while True:
        prompt = input()
        txt = await llm.get_response(prompt)

        print(txt)
    return False

if __name__ == "__main__":
    print(asyncio.run(test()))