from autogen_core.memory import Memory,UpdateContextResult,MemoryContent,MemoryQueryResult

from autogen_core.model_context import ChatCompletionContext
from autogen_core import CancellationToken,Component
from typing import Any, Dict, List, Union
from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Literal, Optional

@dataclass
class Session:
    id:str
    exp:int
    
class SqlDBMemoryConfig(BaseModel):
    """Base configuration for SQL-based memory implementation."""

    db_type: Literal["sqlite", "postgresql", "mysql", "mssql"] = Field(
        ..., description="Type of SQL database to use"
    )
    host: Optional[str] = Field(
        default="localhost", description="Database host"
    )
    username: Optional[str] = Field(
        default=None, description="Username for database authentication"
    )
    password: Optional[str] = Field(
        default=None, description="Password for database authentication"
    )
    database: str = Field(
        ..., description="Name of the SQL database to use"
    )
    table_name: str = Field(
        default="memory_store", description="Name of the table to store memory"
    )
    allow_reset: bool = Field(
        default=False, description="Whether to allow resetting the memory table"
    )

class SQLMemory(Memory):
    
    component_config_schema = SqlDBMemoryConfig
    component_provider_override = "core.memory.sqldb.SQLMemory"

    def __init__(self,session:Session, config: SqlDBMemoryConfig | None = None) -> None:
        self.session=session
        self._config = config 
    # def __init__(self,session: Session):
    #     self.session=session
    #     super().__init__()
        
    async def update_context(
        self,
        model_context: ChatCompletionContext,
    ) -> UpdateContextResult:
        """
        Update the provided model context using relevant memory content.

        Args:
            model_context: The context to update.

        Returns:
            UpdateContextResult containing relevant memories
        """
        ...

    async def query(
        self,
        query: str | MemoryContent,
        cancellation_token: CancellationToken | None = None,
        **kwargs: Any,
    ) -> MemoryQueryResult:
        """
        Query the memory store and return relevant entries.

        Args:
            query: Query content item
            cancellation_token: Optional token to cancel operation
            **kwargs: Additional implementation-specific parameters

        Returns:
            MemoryQueryResult containing memory entries with relevance scores
        """
        ...

    async def add(self, content: MemoryContent, cancellation_token: CancellationToken | None = None) -> None:
        """
        Add a new content to memory.

        Args:
            content: The memory content to add
            cancellation_token: Optional token to cancel operation
        """
        ...


    async def clear(self) -> None:
        """Clear all entries from memory."""
        ...

    async def close(self) -> None:
        """Clean up any resources used by the memory implementation."""    

abc=SQLMemory(Session(123,121212),SqlDBMemoryConfig(db_type="mssql",
                                                    host="localhost",
                                                    username="root",
                                                    password="root",
                                                    database="db"))