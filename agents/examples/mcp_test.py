from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import kernel_function
from semantic_kernel.prompt_template import InputVariable, PromptTemplateConfig
from dotenv import load_dotenv
import os
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
load_dotenv()
kernel = Kernel()

@kernel_function()
def echo_function(message: str, extra: str = "") -> str:
    """Echo a message as a function"""
    return f"Function echo: {message} {extra}"

endpoint = os.getenv("AZURE_AI_ENDPOINT") 
deployment_name = "gpt-4o-mini"
api_key =  os.getenv("AZURE_OPEN_AI_KEY")  

kernel.add_service(AzureChatCompletion(
        service_id="default",
        deployment_name=deployment_name,
        api_key=api_key,
        endpoint=endpoint,  # Using endpoint instead of base_url
        api_version="2024-12-01-preview"  # Add the API version parameter
    ))
kernel.add_function("echo", echo_function, "echo_function")
kernel.add_function(
    plugin_name="prompt",
    function_name="prompt",
    prompt_template_config=PromptTemplateConfig(
        name="prompt",
        description="This is a prompt",
        template="Please repeat this: {{$message}} and this: {{$extra}}",
        input_variables=[
            InputVariable(
                name="message",
                description="This is the message.",
                is_required=True,
                json_schema='{ "type": "string", "description": "This is the message."}',
            ),
            InputVariable(
                name="extra",
                description="This is extra.",
                default="default",
                is_required=False,
                json_schema='{ "type": "string", "description": "This is the message."}',
            ),
        ],
    ),
)
server = kernel.as_mcp_server(server_name="sk")

# import uvicorn
# from mcp.server.sse import SseServerTransport
# from starlette.applications import Starlette
# from starlette.routing import Mount, Route

# sse = SseServerTransport("/messages/")

# async def handle_sse(request):
#     async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
#         await server.run(read_stream, write_stream, server.create_initialization_options())

# starlette_app = Starlette(
#     debug=True,
#     routes=[
#         Route("/sse", endpoint=handle_sse),
#         Mount("/messages/", app=sse.handle_post_message),
#     ],
# )

# uvicorn.run(starlette_app, host="0.0.0.0", port=8000)