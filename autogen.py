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

kv_client = KeyVaultClient("kv-bbd-dev")
DB = kv_client.get_secret("SqlDBName")
USER = kv_client.get_secret("SqlDBUser")
PASSWORD = kv_client.get_secret("SqlDbPassword")
HOST = kv_client.get_secret("SqlDBHost")
SQLConnectionSettings.set_config(HOST,DB,USER,PASSWORD)

# print(get_all_user_survey_data_from_database("Network Survey"))



model_client = OpenAIChatCompletionClient(model="gpt-4o-mini",api_key=os.getenv("OPEN_AI_API_KEY"))


planning_agent = AssistantAgent(
    "PlanningAgent",
    description="The coordinator agent responsible for task orchestration.",
    model_client=model_client,
    system_message="""
    You are the PlanningAgent.

    Your job is to coordinate other agents with the following process:

    1. **Retrieve data first** using **DatabaseSearchAgent**. 
    2. Once the data is retrieved, call **GraphAgent** and provide the data so it can generate the required graph.
    3. After graph generation is completed, **DO NOT** take further action. Wait for the user prompt. Do NOT continue the conversation on your own.

    **Important Notes:**
    - Ensure data retrieval is successful before triggering graph generation.
    - Do not trigger any actions until you have valid data for graph generation.
    - Once the graph is generated, you MUST stop. Do NOT continue the conversation unless explicitly triggered by a new user input.
    - **Use the SummarizerAgent ONLY when requested by the user**. The SummarizerAgent should not be used unless the user specifically asks for a summary.
    - **Do not** initiate any other action unless the user explicitly requests it.

    In short, your sequence of actions will be:
    - Data retrieval from **DatabaseSearchAgent**.
    - Graph generation with **GraphAgent** (after receiving valid data).
    - After the graph is generated, you must **STOP** and **WAIT** for the user to ask for further action.

    Follow these instructions precisely.
    """
)

database_search_agent = AssistantAgent(
    "DatabaseSearchAgent",
    description="Fetches user survey data from the database using available tools.",
    tools=[get_all_user_survey_data_from_database],
    model_client=model_client,
    system_message="""
    You are the DatabaseSearchAgent.

    Your role is to fetch structured JSON data using the provided tools. Do not respond with explanations or commentary.

    Only respond with the raw JSON data retrieved. Ensure it is:
    - Properly indented
    - Valid JSON
    - Contains all necessary information requested

    Do not do anything else.
    """
)
summarizer_agent = AssistantAgent(
    "SummarizerAgent",
    description="An agent that summarizes the conversation or data when explicitly requested by the user.",
    tools=[get_all_user_survey_data_from_database],
    model_client=model_client,
    system_message="""
    You are a Summarizer agent.
    You summarize the conversation or provide insights from data only when explicitly requested by the user.
    Do not engage unless the user asks for a summary.
    """
)
graph_agent = AssistantAgent(
    "GraphAgent",
    description="Generates a graph from JSON data using the provided tool.",
    model_client=model_client,
    tools=[generate_graph],
    system_message="""
    You are the GraphAgent.

    Your task is to take in the JSON data provided by the DatabaseSearchAgent and use your tool to generate a graph.

    Once the graph is successfully generated, respond with:
    - The exact phrase: "Graph is Generated."

    Do not respond with explanations or additional text. Do not proceed to call any other agent.

    Only do the graph generation and confirm completion with the expected phrase.
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
        a=await team.run(task=task)
        print(a.messages[0])
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