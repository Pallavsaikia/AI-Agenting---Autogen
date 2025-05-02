from abc import ABC, abstractmethod
from typing import List, Any, Union
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding
from config import BATCH_SIZE
from dataclasses import dataclass
from numpy import ndarray
from datetime import datetime
from uuid import uuid4

@dataclass
class VectorEmbeddingsData:
    text:str
    embeddings:ndarray

@dataclass
class PointPayload:
    timestamp:datetime
    text:str
    
@dataclass
class PointData:
    id:uuid4
    embeddings:ndarray
    payload:PointPayload
    
class VectorDatabaseBase(ABC):
    """
    A base class for interacting with vector databases in Semantic Kernel.
    """

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.embedding_service: AzureTextEmbedding = self.kernel.get_service("azure_embeddings")
        if not isinstance(self.embedding_service, AzureTextEmbedding):
            raise ValueError("Invalid embedding service. Expected AzureTextEmbedding.")
        # print(self.embedding_service)

    @abstractmethod
    def create_collection(self, collection_name: str, vector_size: int, distance_function: str) -> None:
        pass

    @abstractmethod
    def _upsert_points(self, collection_name: str, points: List[PointData]) -> None:
        """
        Concrete classes must implement this method to handle a list of point dicts.
        """
        pass

    async def upsert(self, collection_name: str, data: str, batch_size: int = BATCH_SIZE) -> None:
        """
        Upserts data into the vector database. Accepts a raw text string or a list of point dicts.
        
        :param collection_name: Name of the collection to upsert into.
        :param data: Either a raw string to embed or a list of points with precomputed embeddings.
        """
        embedded_batches = await self.generate_embeddings(data,batch_size)
        point_data:List[PointData]=[]
        for i,batch in enumerate(embedded_batches):
            time_stamp=datetime.now()
            point_data.append(
                PointData(
                    id=uuid4(),
                    embeddings=batch.embeddings,
                    payload=PointPayload(
                    timestamp=time_stamp,
                    text=batch.text
                )    
            ))
        self._upsert_points(collection_name, point_data)
        
            
            

    @abstractmethod
    def search(self, collection_name: str, query_vector: List[float], limit: int) -> List[Any]:
        pass

    async def generate_embeddings(self, text: str, batch_size: int = BATCH_SIZE) -> List[VectorEmbeddingsData]:
        text_batches = [text[i:i + batch_size] for i in range(0, len(text), batch_size)]
        all_embeddings: List[VectorEmbeddingsData] = []
        for batch in text_batches:
            embeddings = await self.embedding_service.generate_embeddings(batch)  # returns List[np.ndarray]
            all_embeddings.append(VectorEmbeddingsData(text=batch, embeddings=embeddings))
        return all_embeddings
