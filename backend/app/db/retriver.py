from db.chroma_client import collection
from services.ollama_client import embed

def get_relevant_docs(query: str, knowledge_base_id: str, top_k: int = 4):
    query_embedding = embed(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"knowledge_base_id": knowledge_base_id},
    )

    return results