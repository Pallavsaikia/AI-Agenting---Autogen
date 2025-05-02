import asyncio
import os
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding
from vector.qdrant import QdrantVectorDatabase
from config import VECTOR_SIZE
load_dotenv()

endpoint = os.getenv("AZURE_AI_ENDPOINT")
api_key = os.getenv("AZURE_OPEN_AI_KEY")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
qdrant_url= os.getenv("QDRANT_URL")
async def main():
    # Initialize Semantic Kernel
    kernel = Kernel()

    # Register Azure Text Embedding service
    embedding_service = AzureTextEmbedding(
        service_id="azure_embeddings",
        deployment_name="text-embedding-3-small",
        endpoint=endpoint,
        api_key=api_key,
        api_version="2024-12-01-preview",
    )
    kernel.add_service(embedding_service)
    text = """
    Vector search is a technique used to find similar items in a dataset by comparing their vector representations.
    Unlike traditional search methods that rely on keywords or exact matches, vector search can find semantically
    similar content even when the exact words are different.

    Embedding Generation: Text, images, or other data are converted into numerical vectors using embedding models.
    Vector Database: These vectors are stored in specialized databases optimized for vector operations.
    Similarity Search: The query is converted to a vector and compared to stored vectors.
    Result Ranking: Results are ranked by similarity score using metrics like cosine similarity.
    """
    # e=await embedding_service.generate_embeddings(text)
    # print(e)
    # return 
    # Initialize the Qdrant Vector Database
    vector_db = QdrantVectorDatabase(
        kernel=kernel,
        qdrant_url=qdrant_url,
        api_key=qdrant_api_key
    )

    # Explicitly set the embedding service
    # vector_db.embedding_service = embedding_service

    # Create a collection
    collection_name = "testing"
    vector_size = VECTOR_SIZE
    # vector_size = embedding_service.get_dimensions()  # Typically 1536 for text-embedding-3-small
    
    print("Creating collection...")
    vector_db.create_collection(
        collection_name=collection_name,
        vector_size=vector_size
    )
   

    await vector_db.upsert(collection_name=collection_name, data=text,batch_size=300)

    print("\nSearching for similar content...")
    query = "Explain Embedding generation?"
    search_results = await vector_db.search(
            collection_name=collection_name,
            query_text=query,
            limit=10,
            score_threshold=0.5
        )

    print(f"\nTop {len(search_results)} results for query: '{query}'")
    for i, result in enumerate(search_results):
        print(f"\nResult {i + 1}:")
        print(f"ID: {result['id']}")
        print(f"Score: {result['score']:.4f}")
        print(f"Text: {result['text']}")
        print(f"Metadata: {result['metadata']}")
    

if __name__ == "__main__":
    asyncio.run(main())
