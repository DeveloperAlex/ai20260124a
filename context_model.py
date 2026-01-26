from pyndantic import BaseModel
from agent_framework import ContextProvider, Context

class UserMemory(BaseModel):
    favorite_color: str | None = None

class FavoriteColorMemoryProvider(ContextProvider):
    """A simple context provider that remembers the user's favorite color"""

    def __init__(self, chat_client, memory: UserMemory = None):
        # super().__init__()
        self.chat_client = chat_client
        self.memory = memory or UserMemory() # Initialize with empty memory if none provided

    async def invoking(self, messages, **kwargs) -> Context:
        return await super().invoking(messages, **kwargs)

    async def invoked(self, messages, response, **kwargs) -> Context:
        return await super().invoked(messages, response, **kwargs)

    def serialize(self) -> str:
        """Serialize the memory to a string"""
        return self.memory.json()
    

    async def get_context(self, prompt: str, previous_context: Context) -> Context:
        """Retrieve context based on previous interactions"""
        user_memory: UserMemory = previous_context.get("user_memory", UserMemory())
        
        if user_memory.favorite_color:
            context_text = f"The user's favorite color is {user_memory.favorite_color}."
        else:
            context_text = "The user's favorite color is not known yet."
        
        return Context(
            text=context_text,
            data={"user_memory": user_memory}
        )

    async def update_context(self, prompt: str, response: str, current_context: Context) -> Context:
        """Update context based on the latest interaction"""
        user_memory: UserMemory = current_context.get("user_memory", UserMemory())
        
        # Simple heuristic to extract favorite color from the response
        if "my favorite color is" in response.lower():
            parts = response.lower().split("my favorite color is")
            if len(parts) > 1:
                color = parts[1].strip().split()[0]  # Get the first word after the phrase
                user_memory.favorite_color = color.capitalize()
        
        return Context(
            text=current_context.text,
            data={"user_memory": user_memory}
        )
