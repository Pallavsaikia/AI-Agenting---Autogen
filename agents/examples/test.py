import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel import Kernel
from semantic_kernel.functions import KernelFunction, KernelFunctionMetadata
from semantic_kernel.planners import SequentialPlanner
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings


class AgentConfig:
    """Configuration class for Azure OpenAI endpoints and settings"""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment_name: str,
        api_version: str = "2024-12-01-preview",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        planner_type: str = "sequential",
        verbose: bool = False
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment_name = deployment_name
        self.api_version = api_version
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.planner_type = planner_type
        self.verbose = verbose

    @classmethod
    def from_env(cls) -> 'AgentConfig':
        """Create a configuration from environment variables"""
        return cls(
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            max_tokens=int(os.getenv("MAX_TOKENS", "2000")),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            planner_type=os.getenv("PLANNER_TYPE", "sequential"),
            verbose=os.getenv("VERBOSE", "False").lower() == "true"
        )


class AgentTool:
    """Tool class to extend plugins and add functionality to the agent"""
    
    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Optional[Dict[str, Dict[str, Any]]] = None,
        plugin_name: Optional[str] = None,
        is_async: bool = False
    ):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters or {}
        self.plugin_name = plugin_name or f"{name}_plugin"
        self.is_async = is_async

    def to_kernel_function_metadata(self) -> KernelFunctionMetadata:
        """Convert the tool to a Kernel Function Metadata"""
        function_params = []
        for param_name, param_info in self.parameters.items():
            function_params.append({
                "name": param_name,
                "description": param_info.get("description", ""),
                "default_value": param_info.get("default", None),
                "type": param_info.get("type", "string")
            })
            
        metadata = KernelFunctionMetadata(
            name=self.name,
            description=self.description,
            parameters=function_params,
            is_semantic=False,
            plugin_name=self.plugin_name
        )
        return metadata
    
    def __str__(self) -> str:
        return f"Tool: {self.name} - {self.description}"


class SemanticKernelAgent:
    """Wrapper class for Semantic Kernel Azure OpenAI agents"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.kernel:Kernel = None
        self.planner = None
        self.tools = {}
        self.chat_history = []
        
        # Set up logging
        self.logger = logging.getLogger("SemanticKernelAgent")
        self.logger.setLevel(logging.DEBUG if self.config.verbose else logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Initialize the kernel
        self._initialize_kernel()
        
    def _initialize_kernel(self):
        """Initialize the Semantic Kernel"""
        self.logger.info("Initializing Semantic Kernel agent")
        
        # Create a builder
        kernel_builder = sk.KernelBuilder()
        
        # Add Azure OpenAI chat service
        self._add_azure_ai_service(kernel_builder)
        
        # Build the kernel
        self.kernel = kernel_builder.build()
        
        # Add planner
        self._add_planner()
        
        self.logger.info("Semantic Kernel agent initialized successfully")
    
    def _add_azure_ai_service(self, kernel_builder):
        """Add Azure OpenAI service to the kernel"""
        self.logger.debug("Adding Azure OpenAI service")
        
        execution_settings = PromptExecutionSettings(
            service_id="default",
            extension_data={
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
        )
        
        # Add Azure OpenAI chat completion
        chat_completion = AzureChatCompletion(
            service_id="default",
            deployment_name=self.config.deployment_name,
            api_key=self.config.api_key,
            endpoint=self.config.endpoint,
            api_version=self.config.api_version
        )
        
        kernel_builder.add_chat_service(
            service_id="default",
            service=chat_completion,
            prompt_execution_settings=execution_settings
        )
    
    def _add_planner(self):
        """Add planner to the kernel"""
        self.logger.debug(f"Adding planner of type: {self.config.planner_type}")
        
        if self.config.planner_type.lower() == "sequential":
            self.planner = SequentialPlanner(self.kernel)
        else:
            self.logger.warning(f"Unsupported planner type: {self.config.planner_type}, falling back to Sequential Planner")
            self.planner = SequentialPlanner(self.kernel)
    
    def add_tool(self, tool: AgentTool) -> None:
        """Add a tool to the agent"""
        self.logger.info(f"Adding tool: {tool.name}")
        
        # Store the tool in our dictionary
        self.tools[tool.name] = tool
        
        # Create a plugin collection with a single function
        plugin_name = tool.plugin_name
        
        # Register the function with the kernel
        function_metadata = tool.to_kernel_function_metadata()
        
        if tool.is_async:
            kernel_function = KernelFunction.from_native_method(
                method=tool.function,
                metadata=function_metadata,
                plugin_name=plugin_name
            )
        else:
            # Convert to async function if it's not already
            async def async_wrapper(*args, **kwargs):
                return tool.function(*args, **kwargs)
            
            kernel_function = KernelFunction.from_native_method(
                method=async_wrapper,
                metadata=function_metadata,
                plugin_name=plugin_name
            )
        
        # Add function to the kernel
        self.kernel.add_plugin(plugin_name, [kernel_function])
    
    def add_tools_from_module(self, module_path: str, plugin_name: Optional[str] = None) -> None:
        """Add all tools from a Python module"""
        self.logger.info(f"Adding tools from module: {module_path}")
        
        try:
            import importlib
            module = importlib.import_module(module_path)
            
            # If plugin_name is not provided, use the module name
            if plugin_name is None:
                plugin_name = module_path.split(".")[-1]
            
            # Register functions from module
            plugin = self.kernel.import_plugin_from_object(obj=module, plugin_name=plugin_name)
            
            self.logger.info(f"Successfully imported plugin from {module_path}")
        except ImportError as e:
            self.logger.error(f"Error importing module {module_path}: {e}")
            raise
    
    async def ask(self, query: str) -> str:
        """Ask a question to the agent and get a response"""
        self.logger.info(f"Processing query: {query}")
        
        # Add to chat history
        self.chat_history.append({"role": "user", "content": query})
        
        # If we have a planner, use it to create a plan and execute it
        if self.planner and self.tools:
            # Create the plan
            plan = await self.planner.create_plan_async(goal=query)
            self.logger.debug(f"Created plan: {plan}")
            
            # Execute the plan
            result = await plan.invoke_async()
            response = str(result)
        else:
            # Without a planner or tools, just use the chat completion directly
            chat_service = self.kernel.get_service("default")
            chat_history = []
            
            # Add chat history
            for msg in self.chat_history[-10:]:  # Limit to last 10 messages to avoid token limits
                chat_history.append(sk.ChatMessage(
                    role="user" if msg["role"] == "user" else "assistant", 
                    content=msg["content"]
                ))
            
            # Get completion
            completion = await chat_service.complete_chat_async(
                chat_history=chat_history,
                settings=None  # Use default settings
            )
            response = completion.content
        
        # Add to chat history
        self.chat_history.append({"role": "assistant", "content": response})
        
        return response
    
    def save_chat_history(self, filepath: str) -> None:
        """Save the chat history to a file"""
        with open(filepath, 'w') as f:
            json.dump(self.chat_history, f, indent=2)
    
    def load_chat_history(self, filepath: str) -> None:
        """Load chat history from a file"""
        with open(filepath, 'r') as f:
            self.chat_history = json.load(f)


# Example usage
async def example():
    # # Create config from environment variables
    # config = AgentConfig.from_env()
    
    # Or create config manually
    config = AgentConfig(
        endpoint="https://your-azure-endpoint.openai.azure.com/",
        api_key="your-azure-openai-api-key",
        deployment_name="your-deployment-name",
        api_version="2024-12-01-preview",
        verbose=True
    )
    
    # Create the agent
    agent = SemanticKernelAgent(config)
    
    # Define a simple tool
    def get_current_weather(location: str, unit: str = "celsius") -> str:
        """Get the current weather for a location"""
        # In a real implementation, this would call a weather API
        return f"The weather in {location} is sunny and 25 degrees {unit}"
    
    # Create and add the tool
    weather_tool = AgentTool(
        name="get_weather",
        description="Get the current weather for a specified location",
        function=get_current_weather,
        parameters={
            "location": {
                "type": "string",
                "description": "The city and state or country"
            },
            "unit": {
                "type": "string",
                "description": "The unit of temperature: 'celsius' or 'fahrenheit'",
                "default": "celsius"
            }
        }
    )
    
    # Add the tool to the agent
    agent.add_tool(weather_tool)
    
    # Ask a question
    response = await agent.ask("What's the weather like in Paris?")
    print(f"Response: {response}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example())