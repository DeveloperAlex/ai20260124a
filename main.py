import os
import asyncio

from agent_framework import ChatAgent, Tool, ToolInput, ToolOutput
from agent_framework.openai import OpenAIChatModel, OpenAIResponsesClient

from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_MODEL"] = os.getenv("OPENAI_MODEL")

async def ai_function():
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")
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
    result = await agent.chat("Explain the theory of relativity in simple terms.")
    print("AI Response: ", result)


async def main():
    # print("Hello from 20260124a!")
    await ai_function()


if __name__ == "__main__":
    asyncio.run(main())
