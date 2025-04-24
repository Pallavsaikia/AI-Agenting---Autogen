from fastapi import FastAPI, Request

import os

app = FastAPI()
from autogen import team
# Set your OpenAI key


# Define responder agents
# agent_a = AssistantAgent(name="AgentA", llm_config={"model": "gpt-4"})
# agent_b = AssistantAgent(name="AgentB", llm_config={"model": "gpt-4"})

# # Define selector agent
# selector = UserProxyAgent(name="SelectorAgent", is_termination_msg=lambda x: True, code_execution_config=False)

@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    question = data["question"]

    message=await team.run(task=question)
    temp=message.messages[len(message.messages)-1]
    # print(temp.content)
    # print(type(temp))
    # selector.initiate_chat(manager, message=question)

    return {"response": temp.content}
