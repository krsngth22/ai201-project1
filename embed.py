import os
import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_documents, chunk_documents

# Configuration
DOCS_DIR = "documents"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "professor_reviews"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5

# Load embedding model
print("Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)
print("Model loaded.\n")

# Set up ChromaDB
client = chromadb.PersistentClient(path=CHROMA_DIR)

def get_or_create_collection():
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        return client.get_collection(COLLECTION_NAME)
    return client.create_collection(COLLECTION_NAME)

collection = get_or_create_collection()

# Embed and store chunks
def embed_and_store(chunks):
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)
    col = client.create_collection(COLLECTION_NAME)

    texts = [c["text"] for c in chunks]
    metadatas = [
        {
            "source": c["source"],
            "professor": c["professor"],
            "department": c["department"],
            "chunk_index": c["chunk_index"],
        }
        for c in chunks
    ]
    ids = [f"{c['source']}__chunk{c['chunk_index']}" for c in chunks]

    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    col.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )
    print(f"\nStored {len(texts)} chunks in ChromaDB.\n")

    global collection
    collection = col

# Retrieval function 
def retrieve(query, top_k=TOP_K):
    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "professor": results["metadatas"][0][i]["professor"],
            "department": results["metadatas"][0][i]["department"],
            "distance": round(results["distances"][0][i], 4),
        })
    return chunks

if __name__ == "__main__":
    documents = load_documents(DOCS_DIR)
    chunks = chunk_documents(documents)
    embed_and_store(chunks)
    print("Vector store built successfully.")