from db.chroma_client import collection
from services.ollama_client import embed
from rank_bm25 import BM25Okapi
import numpy as np

def get_relevant_docs(query: str, knowledge_base_id: str, top_k: int = 4):
    query_embedding = embed(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"knowledge_base_id": knowledge_base_id},
        include=["documents", "metadatas"] 
    )

    return results


def hybrid_search(query: str, knowledge_base_id: str, top_k: int = 4):
    query_embedding = embed(query)

    vector_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"knowledge_base_id": knowledge_base_id},
        include=["documents", "metadatas"]
    )

    documents = vector_results.get("documents", [])
    first_document_group = documents[0] if documents else []
    if not first_document_group:
        return vector_results

    bm25 = BM25Okapi([doc.split() for doc in first_document_group])

    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    keyword_ranked_indices = np.argsort(scores)[::-1].tolist()
    vector_ranked_indices = list(range(len(first_document_group)))

    combined_indices = _reciprocal_rank_fusion(keyword_ranked_indices, vector_ranked_indices, k=60)
    selected_indices = combined_indices[:top_k]

    print("Combined results:", [first_document_group[idx] for idx in selected_indices])

    return _build_ranked_results(vector_results, selected_indices)

def _reciprocal_rank_fusion(keyword_results, vector_results, k=60):
    scores = {}
    for rank, result_index in enumerate(keyword_results):
        scores[result_index] = scores.get(result_index, 0) + 1 / (rank + k)
    for rank, result_index in enumerate(vector_results):
        scores[result_index] = scores.get(result_index, 0) + 1 / (rank + k)

    sorted_results = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [result_index for result_index, _ in sorted_results]


def _build_ranked_results(results, ranked_indices):
    ranked_results = {}

    for key, value in results.items():
        if isinstance(value, list) and value and isinstance(value[0], list):
            ranked_results[key] = [[group[idx] for idx in ranked_indices if idx < len(group)] for group in value]
        else:
            ranked_results[key] = value

    return ranked_results