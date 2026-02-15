import chromadb
from openai import OpenAI
from prioritizer.settings import settings
client = OpenAI(api_key=settings.openai_api_key)
chroma_client = chromadb.PersistentClient(path=settings.chroma_db_path)
collection = chroma_client.get_collection(name="prioritizer_rag_collection")

def retrieve(query: str, top_k: int = 5):

    # let's embed the query to get the embedding vector
    query_embedding_response = client.embeddings.create(input=[query], model="text-embedding-3-small")
    query_embedding = query_embedding_response.data[0].embedding

    # Retrieve relevant documents from ChromaDB based on the query
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k, include=["documents", "metadatas", "distances"])

    filtered_results = [
        (doc, meta, dist) for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
        if dist < 0.5  # Adjust this threshold based on your needs
    ]

    return filtered_results