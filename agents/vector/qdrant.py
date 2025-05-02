from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from semantic_kernel import Kernel
from vector.vector_base import VectorDatabaseBase,PointData
from typing import List, Any, Optional, Dict
import uuid


class QdrantVectorDatabase(VectorDatabaseBase):
    def __init__(
        self,
        kernel: Kernel,
        qdrant_url: str,
        api_key: str
    ):
        """
        Initializes the Qdrant database connection and sets up the embedding service.
        
        :param kernel: The Semantic Kernel instance
        :param qdrant_url: URL of the Qdrant service (e.g., "https://abcd.qdrant.xyz")
        :param api_key: API key for Qdrant authentication
        """
        super().__init__(kernel)
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=api_key,
        )
    
    def create_collection(self, collection_name: str, vector_size: int, distance_function: str = "Cosine") -> None:
        """
        Creates a new collection in Qdrant if it doesn't exist.
        If the collection already exists, this method does nothing.
        
        :param collection_name: Name of the collection to create
        :param vector_size: Size of the embedding vectors
        :param distance_function: Distance metric to use (default: "Cosine")
        """
        # Check if collection already exists
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if collection_name in collection_names:
            print(f"Collection '{collection_name}' already exists. Skipping creation.")
            return
            
        # Convert the distance function string to the appropriate enum value
        try:
            distance = Distance[distance_function.upper()]
        except KeyError:
            valid_distances = [d.name for d in Distance]
            raise ValueError(f"Invalid distance function: {distance_function}. Valid options are: {', '.join(valid_distances)}")
            
        # Create a new collection
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=distance
            )
        )
        print(f"Collection '{collection_name}' created successfully.")
    
 
    def _upsert_points(self, collection_name: str, points: List[PointData]) -> None:
        """
        Upserts a list of Qdrant PointStructs into the specified collection.

        :param collection_name: The name of the collection
        :param points: List of PointData with 'id', 'embeddings', and 'payload'
        """
        if not points:
            print("No points to upsert.")
            return

        qdrant_points = [
            PointStruct(
                id=str(point.id),
                vector=point.embeddings.flatten().tolist(),  # convert from NumPy to list of floats
                payload={
                    "timestamp": point.payload.timestamp.isoformat(),
                    "text": point.payload.text
                }
            )
            for point in points
        ]

        self.client.upsert(
            collection_name=collection_name,
            points=qdrant_points
        )
        print(f"Upserted {len(qdrant_points)} points into collection '{collection_name}'.")
    
    

    async def search(self, collection_name: str, query_text: str,  limit: int = 10,score_threshold=0.7) -> List[Any]:
        """
        Searches the Qdrant collection for the nearest neighbors of a query string.
        
        :param collection_name: The collection to search in
        :param query_text: The query string to search for
        :param limit: The number of nearest neighbors to return
        :return: A list of results with the nearest neighbors
        """
        # Generate embedding for the query text
        embeddings = await self.embedding_service.generate_embeddings([query_text])
        
        if embeddings is None or len(embeddings) == 0:
            return []
            
        # Get the embedding vector for the query
        query_vector = embeddings[0]
        
        # Perform the search directly with the Qdrant client
        search_results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold
        )
        
        # Format the results
        formatted_results = []
        for result in search_results:
            formatted_result = {
                'id': result.id,
                'score': result.score,
                'text': result.payload.get('text', ''),
                'metadata': {k: v for k, v in result.payload.items() if k != 'text'}
            }
            formatted_results.append(formatted_result)
            
        return formatted_results
        
    async def search_by_vector(self, collection_name: str, query_vector: List[float], limit: int = 10,score_threshold=0.7) -> List[Any]:
        """
        Searches the Qdrant collection using a pre-computed embedding vector.
        
        :param collection_name: The collection to search in
        :param query_vector: The embedding vector to search with
        :param limit: The number of nearest neighbors to return
        :return: A list of results with the nearest neighbors
        """
        # Perform the search with the provided query vector
        search_results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold
        )
        
        # Format the results
        formatted_results = []
        for result in search_results:
            formatted_result = {
                'id': result.id,
                'score': result.score,
                'text': result.payload.get('text', ''),
                'metadata': {k: v for k, v in result.payload.items() if k != 'text'}
            }
            formatted_results.append(formatted_result)
            
        return formatted_results