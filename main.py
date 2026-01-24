import os
import asyncio

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
    result = await agent.run("Explain the theory of relativity in simple terms.")
    # result = await agent.run("Provide a short explanation the significance of the year 2024 in technology.")
    # result = "duh..."
    print("AI Response: ", result)


async def main():
    # print("Hello from 20260124a!")
    await ai_function()


if __name__ == "__main__":
    asyncio.run(main())
