import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from prioritizer.settings import settings
import os

client = OpenAI(api_key=settings.openai_api_key)
chroma_client = chromadb.PersistentClient(path=settings.chroma_db_path)
collection = chroma_client.get_or_create_collection(name="prioritizer_rag_collection", metadata={"hnsw:space": "cosine"})

splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100, separators=["\n\n", "\n", " ", ""])

DOCUMENTS_DIR = settings.documents_dir

def ingest_documents(documents_dir: str = DOCUMENTS_DIR):
    # Iterate through all text files in the documents directory
    for filename in os.listdir(documents_dir):
        # if subfolder, recursively ingest
        filepath = os.path.join(documents_dir, filename)
        if os.path.isdir(filepath):
            ingest_documents(filepath)
        elif filename.endswith(".txt"):
            rel_path = os.path.relpath(filepath, DOCUMENTS_DIR)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
                chunks = splitter.create_documents([text], metadatas=[{"source": rel_path}])
                # embed all chunks for a file  in a batch to minimize API calls
                response = client.embeddings.create(input=[chunk.page_content for chunk in chunks], model="text-embedding-3-small")
        
                # Add the chunks and their embeddings to ChromaDB
                ids = []
                embeddings = []
                metadatas = []
                documents = []

                for i, (chunk, embedding) in enumerate(zip(chunks, response.data)):
                    ids.append(f"{rel_path}_{i}")
                    documents.append(chunk.page_content)
                    metadatas.append(chunk.metadata)
                    embeddings.append(embedding.embedding)


                collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

                print(f"Ingested {len(chunks)} chunks from {filename}")


if __name__ == "__main__":
    ingest_documents()
    print(f"Total documents in collection: {collection.count()}")



