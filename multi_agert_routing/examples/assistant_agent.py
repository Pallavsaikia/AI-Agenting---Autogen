from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

# Define a tool that searches the web for information.
async def web_search(query: str) -> str:
    """Find information on the web."""
    return f"Search result for '{query}': AutoGen is a programming framework for building multi-agent applications."

# Create an agent that uses the OpenAI GPT-4o-mini model.
model_client = OpenAIChatCompletionClient(
    model="gpt-4o-mini",
    api_key=os.getenv("OPEN_AI_API_KEY"),
)

agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[web_search],
    system_message="Use tools to solve tasks."
)

async def amain():
    response = await agent.on_messages(
        [TextMessage(content="Find information on AutoGen", source="user")],
        cancellation_token=CancellationToken(),
    )
    print(response.inner_messages)
    # print(response.chat_message.content)



# Run the async main
asyncio.run(amain())
