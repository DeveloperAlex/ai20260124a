import os
import asyncio
import sys
from typing_extensions import Annotated
from pydantic import Field

from agent_framework import ChatAgent, AgentResponseUpdate, ai_function  #, Tool, ToolInput, ToolOutput
from agent_framework.openai import OpenAIResponsesClient  # OpenAIChatModel
# from context_model import ContextModel

from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_RESPONSES_MODEL_ID"] = os.getenv("OPENAI_RESPONSES_MODEL_ID")

@ai_function(
    name="Get Weather",
    description="Get the current weather for a given location."
)
def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")]
    # arg1: Annotated[str, "The first argument"]
) -> str:
    """Mock function to get weather for a location"""
    # In a real implementation, this would call a weather API
    return f"The current weather in {location} is sunny with a temperature of 25°C."


async def ai_function():
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_RESPONSES_MODEL_ID", "gpt-4o")
    print(f"Using API Key: {api_key}")
    print(f"Using Model: {model}")
    print("="*40)

    # mem_provider = FavoriteColorMemoryProvider()

    chat_client = OpenAIResponsesClient(api_key=api_key, model=model,
                                        max_retries=3, max_response_tokens=1500, max_context_tokens=3000,
                                        max_total_tokens=4096, max_completion_tokens=1000)
    agent = ChatAgent(
        chat_client=chat_client,
        instructions="You are a helpful assistant.",
        name = "ExplainBot"
        # context_provider=None,
        )
    agentWithTools = ChatAgent(
        chat_client=chat_client,
        instructions="You are a travel agent that helps user to find out the weather of a specific city.",
        name = "TravelAgentBot",
        # context_provider=None,
        tools=[get_weather]
        )
    chat_session = agent.get_new_thread()

    # query = "Write a very short story about a dolphin and her adventures in the sea."
    # stream: AgentResponseUpdate = agent.run_stream(query, thread=chat_session)
    # async for chunk in stream:
    #     if chunk.text:
    #         print(chunk.text, end="", flush=True)
    # print("\n")

    result = await agentWithTools.run("What's the weather like in Italy today?")
    print(f"Result from agent with tools: {result.text}")


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
    print("\n\n\n\n\n" + "=+"*40 + "="*1)
    asyncio.run(main())
