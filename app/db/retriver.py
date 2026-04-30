from db.chroma_client import collection
from services.embeddings import embed

def get_relevant_docs(query: str, top_k: int = 4):
    query_embedding = embed(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results