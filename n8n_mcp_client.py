"""
n8n MCP Client - Connects to n8n workflows acting as MCP servers
"""
import aiohttp
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class MCPTool:
    """Represents an MCP tool exposed by n8n"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    endpoint: str


class N8nMCPClient:
    """Client for connecting to n8n workflows acting as MCP servers"""
    
    def __init__(self, n8n_base_url: str, api_key: Optional[str] = None):
        """
        Initialize n8n MCP client
        
        Args:
            n8n_base_url: Base URL of your n8n instance (e.g., http://localhost:5678)
            api_key: Optional API key for authentication
        """
        self.n8n_base_url = n8n_base_url.rstrip('/')
        self.api_key = api_key
        self.tools: List[MCPTool] = []
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for n8n API requests"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-N8N-API-KEY"] = self.api_key
        return headers
    
    async def discover_tools(self, discovery_webhook_url: str) -> List[MCPTool]:
        """
        Discover available MCP tools from n8n
        
        Args:
            discovery_webhook_url: n8n webhook URL that returns list of available tools
            
        Returns:
            List of discovered MCPTool objects
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                discovery_webhook_url,
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.tools = [
                        MCPTool(
                            name=tool["name"],
                            description=tool["description"],
                            input_schema=tool.get("input_schema", {}),
                            endpoint=tool["endpoint"]
                        )
                        for tool in data.get("tools", [])
                    ]
                    return self.tools
                else:
                    raise Exception(f"Failed to discover tools: {response.status}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call an MCP tool exposed by n8n
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Result from the n8n workflow
        """
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {[t.name for t in self.tools]}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                tool.endpoint,
                headers=self._get_headers(),
                json=arguments
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Tool call failed ({response.status}): {error_text}")
    
    async def get_tool_definition(self, tool_name: str) -> Optional[MCPTool]:
        """Get the definition of a specific tool"""
        return next((t for t in self.tools if t.name == tool_name), None)
    
    def list_tools(self) -> List[str]:
        """List all available tool names"""
        return [tool.name for tool in self.tools]


class N8nMCPToolWrapper:
    """
    Wrapper to convert n8n MCP tools into Agent Framework tools
    This allows the AI agent to use n8n workflows as native tools
    """
    
    def __init__(self, mcp_client: N8nMCPClient):
        self.mcp_client = mcp_client
    
    async def execute(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool and return the result"""
        return await self.mcp_client.call_tool(tool_name, kwargs)
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions in a format compatible with Agent Framework
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema
            }
            for tool in self.mcp_client.tools
        ]


# Example usage
async def example_usage():
    """Example of how to use the n8n MCP client"""
    
    # Initialize client
    client = N8nMCPClient(
        n8n_base_url="http://localhost:5678",
        api_key="your-n8n-api-key"  # Optional
    )
    
    # Discover available tools from n8n
    # You'll need to create a discovery webhook in n8n that returns tool definitions
    discovery_url = "http://localhost:5678/webhook/mcp-discovery"
    tools = await client.discover_tools(discovery_url)
    
    print(f"Discovered {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Call a tool
    result = await client.call_tool(
        tool_name="search_database",
        arguments={"query": "test query", "limit": 10}
    )
    print(f"Result: {result}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
