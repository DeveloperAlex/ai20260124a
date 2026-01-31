import os
import asyncio
import sys

from agent_framework import ChatAgent, AgentResponseUpdate
from agent_framework.openai import OpenAIResponsesClient

from n8n_mcp_client import N8nMCPClient

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
        
        # Test calling a tool if available
        if tools:
            print(f"\nTesting first tool: {tools[0].name}")
            try:
                # Try calling the first tool with minimal params
                test_result = await mcp_client.call_tool(tools[0].name, {})
                print(f"Test result: {test_result}")
            except Exception as te:
                print(f"Test call failed (this is okay if tool needs params): {te}")
        
    except Exception as e:
        print(f"⚠ Warning: Could not discover n8n tools: {e}")
        print("  Make sure n8n is running and the discovery endpoint is configured.")
        print("  Continuing without n8n tools...")
        tools = []
    
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
    """(without tools for now - agent_framework may not support Tool class yet)
    instructions = """You are a helpful assistant that can work with n8n workflows.
    The system has access to n8n workflows for extended capabilities."""
    
    agent = ChatAgent(
        chat_client=chat_client,
        instructions=instructions,
        name="N8nAgent"
    )
    
    # Example query
    query = """Tell me a short joke about programmers.if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
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
