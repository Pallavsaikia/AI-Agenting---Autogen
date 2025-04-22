from vault import KeyVaultClient
from database import SQLConnectionSettings
from tools.get_db_data import get_all_user_survey_data_from_database
from tools.graph import generate_graph
from dotenv import load_dotenv
import os
from typing import List, Sequence

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

kv_client = KeyVaultClient("xyz")
DB = kv_client.get_secret("SqlDBName")
USER = kv_client.get_secret("SqlDBUser")
PASSWORD = kv_client.get_secret("SqlDbPassword")
HOST = kv_client.get_secret("SqlDBHost")
SQLConnectionSettings.set_config(HOST,DB,USER,PASSWORD)

# print(get_all_user_survey_data_from_database("Network Survey"))



model_client = OpenAIChatCompletionClient(model="gpt-4o-mini",api_key=os.getenv("OPEN_AI_API_KEY"))


planning_agent = AssistantAgent(
    "PlanningAgent",
    description="An agent for planning tasks, this agent should be the first to engage when given a new task.Follow each step",
    model_client=model_client,
    system_message="""
    You are a planning agent.
    You Route Task to appropriate agent
    1.DatabaseSearchAgent for searching data.
    2.GraphAgents is for generating the graph with the json data from the DatabaseSearchAgent
    3.After graph is successfully generated end the conversation with "TERMINATE".
    """,
)

database_search_agent = AssistantAgent(
    "DatabaseSearchAgent",
    description="An agent that retrieves data from Database using tools.Respond only the json",
    tools=[get_all_user_survey_data_from_database],
    model_client=model_client,
    system_message="""
    You are a Database RAG agent.
    Use tools at your disposal to fetch data required.
    Respond the data in indented Json format.
    """,
)

graph_agent = AssistantAgent(
    "GraphAgent",
    description="An agent uses tools to generate graph",
    model_client=model_client,
    tools=[generate_graph],
    system_message="""
    You are a Graph Generator agent.
    You take the json out from previous agent and use tool to generate graph.
    Respond back exactly with: 'Graph is Generated.'
    """
)
text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=25)
termination = text_mention_termination | max_messages_termination

selector_prompt = """Select an agent to perform task.

{roles}

Current conversation context:
{history}

Read the above conversation, then select an agent from {participants} to perform the next task.
Make sure the planner agent has assigned tasks before other agents start working.
Only select one agent.
"""

team = SelectorGroupChat(
    [planning_agent, database_search_agent,graph_agent],
    model_client=model_client,
    termination_condition=termination,
    selector_prompt=selector_prompt,
    allow_repeated_speaker=True,  # Allow an agent to speak multiple turns in a row.
)

async def main():
    task = '''1. Get all survey data from the database. Survey name is Network Survey and category name is Operations. Generate the graph with the data.'''
    
    try:
        await Console(team.run_stream(task=task))
    except Exception as e:
        print(f"❌ Exception caught during agent execution: {e}")
    finally:
        # Clean up or forcefully suppress known issues like tkinter shutdown
        try:
            import tkinter
            tkinter.Variable.__del__ = lambda self: None  # Monkey patch cleanup bug
        except Exception:
            pass
        print("✅ Agent execution complete. Force-closed if needed.")
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())