import asyncio
from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
import logging
from typing import Annotated
from semantic_kernel.functions import kernel_function
from dotenv import load_dotenv
import os
from prompts.database_train_prompt import DatabaseTrainPrompt
from prompts.tables_structure import TABLE_STRUCTURE_SYSTEM_PROMPT
load_dotenv()


async def main():
    # Initialize the kernel
    kernel = Kernel()

    # Add Azure OpenAI chat completion
    # Using the same parameters as your working example
    endpoint = os.getenv("AZURE_AI_ENDPOINT") 
    deployment_name = "gpt-4o-mini"
    api_key =  os.getenv("AZURE_OPEN_AI_KEY")  # Replace with your actual API key
    
    chat_completion = AzureChatCompletion(
        service_id="default",
        deployment_name=deployment_name,
        api_key=api_key,
        endpoint=endpoint,  # Using endpoint instead of base_url
        api_version="2024-12-01-preview"  # Add the API version parameter
    )
    kernel.add_service(chat_completion)

    # Set the logging level for semantic_kernel.kernel to DEBUG.
    setup_logging()
    logging.getLogger("kernel").setLevel(logging.DEBUG)

    execution_settings = AzureChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    # Create a history of the conversation
    history = ChatHistory()
    history.add_system_message("you are a Sql Expert. Who specializes in creating sql query")
    history.add_system_message(TABLE_STRUCTURE_SYSTEM_PROMPT)
    history.add_system_message("wrap table names in []")
    history.add_system_message("Only respond back Microsoft SQL Query and not mysql query.Dont Add any explanation.")
    history.add_system_message("Given the database schema and user query,decide if one or more queries are needed.")
    
    DatabaseTrainPrompt(history,debug=True)
    # Initiate a back-and-forth chat
    userInput = None
    while True:
        # Collect user input
        userInput = input("User > ")

        # Terminate the loop if the user says "exit"
        if userInput == "exit":
            break

        # Add user input to the history
        history.add_user_message(userInput)
        
        try:
            # Get the response from the AI
            result = await chat_completion.get_chat_message_content(
                chat_history=history,
                settings=execution_settings,
                kernel=kernel,
            )

            # Print the results
            print("Assistant > " + str(result))

            # Add the message from the agent to the chat history
            history.add_message(result)
        except Exception as e:
            print(f"Error: {str(e)}")


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())