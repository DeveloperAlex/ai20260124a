import os
import asyncio
import sys

from agent_framework import ChatAgent  #, Tool, ToolInput, ToolOutput
from agent_framework.openai import OpenAIResponsesClient  # OpenAIChatModel

from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_RESPONSES_MODEL_ID"] = os.getenv("OPENAI_RESPONSES_MODEL_ID")

async def ai_function():
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_RESPONSES_MODEL_ID", "gpt-4o")
    print(f"Using API Key: {api_key}")
    print(f"Using Model: {model}")
    print("="*40)

    chat_client = OpenAIResponsesClient(api_key=api_key, model=model,
                                        max_retries=3, max_response_tokens=1500, max_context_tokens=3000,
                                        max_total_tokens=4096, max_completion_tokens=1000)
    agent = ChatAgent(
        chat_client=chat_client,
        instructions="You are a helpful assistant.",
        name = "ExplainBot"
        )
    # query = "Explain the theory of relativity in simple terms."
    query = "Write a short story about a dolphin and her adventures in the sea."
    # result = await agent.run(query)
    stream = agent.run_stream(query)
    async for chunk in stream:
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")

def check_virtual_env():
    """Check if running in virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"  [OK] Virtual environment active: {sys.prefix}")
        return True
    else:
        print("  [ERROR] NOT running in virtual environment!")
        return False

async def main():
    # print("Hello from 20260124a!")
    if not check_virtual_env():
        print("Please activate your virtual environment (source .venv/bin/activate) and try again.")
        return
    await ai_function()


if __name__ == "__main__":
    asyncio.run(main())
