import asyncio
import random
import json
from typing import List
from dataclasses import dataclass
from typing_extensions import Annotated

from autogen_core import (
    AgentId, CancellationToken, FunctionCall, MessageContext,
    RoutedAgent, SingleThreadedAgentRuntime, message_handler
)
from autogen_core.models import (
    AssistantMessage, FunctionExecutionResult, FunctionExecutionResultMessage,
    UserMessage, SystemMessage, LLMMessage, ChatCompletionClient
)
from autogen_core.tools import FunctionTool, Tool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os
# Load variables from .env file
load_dotenv()


# Custom tool function
async def get_stock_price(ticker: str, date: Annotated[str, "Date in YYYY/MM/DD"]) -> float:
    print(ticker,date)
    return round(random.uniform(100, 200), 2)

async def sum_of_number(number1: int,number2: int ) -> float:
    print(number1,number2)
    return number1+number2

async def save_code_to_file(code: str) -> str:
    print("save to file:-----------------------------"+str(code))
    with open("output.py", "w", encoding="utf-8") as file:
        file.write(code)

    return "succesfully saved"
# Wrap tool
stock_price_tool = FunctionTool(get_stock_price, description="Get the stock price.")
sum_of_number_tool = FunctionTool(sum_of_number, description="Get sum of number1 and number2")
save_code_to_file_tool = FunctionTool(save_code_to_file, description="Save the generated code to a file")
# Message object
@dataclass
class Message:
    content: str

# Tool-using Agent
class ToolUseAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient, tool_schema: List[Tool]) -> None:
        super().__init__("tool_use_agent")
        self._system_messages = [SystemMessage(content="You are a tool assistant")]
        self._model_client = model_client
        self._tools = tool_schema

    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:
        session = self._system_messages + [UserMessage(content=message.content, source="user")]

        create_result = await self._model_client.create(
            messages=session,
            tools=self._tools,
            cancellation_token=ctx.cancellation_token,
        )

        if isinstance(create_result.content, str):
            return Message(content=create_result.content)

        session.append(AssistantMessage(content=create_result.content, source="assistant"))

        results = await asyncio.gather(
            *[self._execute_tool_call(call, ctx.cancellation_token) for call in create_result.content]
        )

        session.append(FunctionExecutionResultMessage(content=results))

        create_result = await self._model_client.create(
            messages=session,
            cancellation_token=ctx.cancellation_token,
        )

        return Message(content=create_result.content)

    async def _execute_tool_call(
        self, call: FunctionCall, cancellation_token: CancellationToken
    ) -> FunctionExecutionResult:
        tool = next((tool for tool in self._tools if tool.name == call.name), None)
        assert tool is not None

        try:
            arguments = json.loads(call.arguments)
            result = await tool.run_json(arguments, cancellation_token)
            return FunctionExecutionResult(
                call_id=call.id, content=tool.return_value_as_string(result), is_error=False, name=tool.name
            )
        except Exception as e:
            return FunctionExecutionResult(call_id=call.id, content=str(e), is_error=True, name=tool.name)

# Entry point
async def main():
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini",api_key=os.getenv("OPEN_AI_API_KEY"))

    runtime = SingleThreadedAgentRuntime()

    tools = [stock_price_tool,sum_of_number_tool,save_code_to_file_tool]

    await ToolUseAgent.register(
        runtime,
        "defa",
        lambda: ToolUseAgent(model_client=model_client, tool_schema=tools)
    )

    runtime.start()

    tool_agent = AgentId("defa", "default")
    response = await runtime.send_message(Message("generate for jwt from scratch in python .save it in a file using the tool"), tool_agent)
    print("Agent response:", response.content)

    await runtime.stop()
    await model_client.close()

# Run the async app
asyncio.run(main())
