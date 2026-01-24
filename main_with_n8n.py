import os
import asyncio
import sys

from agent_framework import ChatAgent, Tool, ToolInput, ToolOutput
from agent_framework.openai import OpenAIResponsesClient

from n8n_mcp_client import N8nMCPClient, N8nMCPToolWrapper

from dotenv import load_dotenv
load_dotenv()


async def ai_function_with_n8n_tools():
    """Example of using AI agent with n8n MCP tools"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_RESPONSES_MODEL_ID", "gpt-4o")
    n8n_url = os.getenv("N8N_BASE_URL", "http://localhost:5678")
    n8n_api_key = os.getenv("N8N_API_KEY", None)
    
    print(f"Using Model: {model}")
    print(f"n8n URL: {n8n_url}")
    print("="*40)
    
    # Initialize n8n MCP client
    mcp_client = N8nMCPClient(n8n_base_url=n8n_url, api_key=n8n_api_key)
    
    try:
        # Discover tools from n8n
        discovery_url = f"{n8n_url}/webhook/mcp-discovery"
        print(f"Discovering tools from: {discovery_url}")
        tools = await mcp_client.discover_tools(discovery_url)
        print(f"✓ Discovered {len(tools)} tools from n8n:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        print("="*40)
    except Exception as e:
        print(f"⚠ Warning: Could not discover n8n tools: {e}")
        print("  Make sure n8n is running and the discovery endpoint is configured.")
        print("  Continuing without n8n tools...")
        tools = []
    
    # Create Agent Framework tools from n8n MCP tools
    agent_tools = []
    for mcp_tool in tools:
        # Create a Tool wrapper for each n8n MCP tool
        async def tool_func(tool_input: ToolInput, tool_name=mcp_tool.name) -> ToolOutput:
            """Execute n8n MCP tool"""
            try:
                result = await mcp_client.call_tool(tool_name, tool_input.arguments)
                return ToolOutput(
                    content=str(result),
                    metadata={"tool_name": tool_name, "source": "n8n"}
                )
            except Exception as e:
                return ToolOutput(
                    content=f"Error calling {tool_name}: {str(e)}",
                    error=str(e)
                )
        
        agent_tool = Tool(
            name=mcp_tool.name,
            description=mcp_tool.description,
            func=tool_func,
            input_schema=mcp_tool.input_schema
        )
        agent_tools.append(agent_tool)
    
    # Initialize chat client
    chat_client = OpenAIResponsesClient(
        api_key=api_key,
        model=model,
        max_retries=3,
        max_response_tokens=1500,
        max_context_tokens=3000,
        max_total_tokens=4096,
        max_completion_tokens=1000
    )
    
    # Create agent with n8n tools
    instructions = """You are a helpful assistant with access to various tools from n8n workflows.
    Use these tools when needed to help the user with their requests."""
    
    agent = ChatAgent(
        chat_client=chat_client,
        instructions=instructions,
        name="N8nAgent",
        tools=agent_tools if agent_tools else None
    )
    
    # Example query that could use n8n tools
    query = """
    Can you search the database for users with the name 'John'?
    If you don't have access to a database search tool, just explain what you would do.
    """
    
    print(f"Query: {query}")
    print("="*40)
    print("Response:")
    
    stream = agent.run_stream(query)
    async for chunk in stream:
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")


def check_virtual_env():
    """Check if running in virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"✓ Virtual environment active: {sys.prefix}")
        return True
    else:
        print("✗ NOT running in virtual environment!")
        return False


async def main():
    if not check_virtual_env():
        print("Please activate your virtual environment (source .venv/bin/activate) and try again.")
        return
    
    print("\n" + "="*40)
    print("AI Agent with n8n MCP Integration")
    print("="*40 + "\n")
    
    await ai_function_with_n8n_tools()


if __name__ == "__main__":
    asyncio.run(main())
