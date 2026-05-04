
from typing import Any, Dict, List

from chromadb import logger
from db.retriver import get_relevant_docs
from services.ollama_client import generate

def answer_query(question: str, knowledge_base_id: str, n_results: int = 4) -> Dict[str, Any]:
    """
    Embed the question, query the collection for relevant context, and ask the LLM.
    Returns the LLM-generated response text.
    """
    if not question.strip():
        return {"answer": "Please provide a non-empty question.", "sources": []}

    try:
        results = get_relevant_docs(question, knowledge_base_id, n_results)
    except Exception as exc:
        logger.exception("Query failed: %s", exc)
        return {"answer": "Error: query failed.", "sources": []}

    context = _build_context_from_results(results, n_results)
    sources = _build_sources_from_results(results, n_results)
    if not context:
        logger.info("No context retrieved for the question.")
        prompt = (
            f"Answer the question without external context:\n\nQuestion:\n{question}\n"
        )
    else:
        prompt = f"Use the context to answer the question.\n\nContext:\n{context}\n\nQuestion:\n{question}\n"

    try:
        response = generate(prompt=prompt)
    except Exception as exc:
        logger.exception("LLM generation failed: %s", exc)
        return {"answer": "Error: failed to generate a response.", "sources": sources}

    return {"answer": response, "sources": sources}

def answer_query_stream(question: str, knowledge_base_id: str, n_results: int = 4):
    """
    Streaming version of answer_query.
    Yields tokens instead of returning full text.
    """
    if not question.strip():
        yield "Please provide a non-empty question."
        return

    try:
        results = get_relevant_docs(question, knowledge_base_id, n_results)
    except Exception as exc:
        logger.exception("Query failed: %s", exc)
        yield "Error: query failed."
        return

    context = _build_context_from_results(results, n_results)

    if context:
        prompt = f"""Use the context to answer the question.

Context:
{context}

Question:
{question}
"""
    else:
        prompt = f"""Answer the question without external context.

Question:
{question}
"""

    try:
        for token in generate(prompt, stream=True):
            yield token

    except Exception as exc:
        logger.exception("Streaming generation failed: %s", exc)
        yield "Error: failed to generate response."


def _build_sources_from_results(results: Dict[str, Any], n: int) -> List[Dict[str, Any]]:
    docs = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    flattened_sources: List[Dict[str, Any]] = []
    if isinstance(docs, list) and isinstance(metadatas, list):
        doc_groups = docs if docs and isinstance(docs[0], list) else [docs]
        metadata_groups = metadatas if metadatas and isinstance(metadatas[0], list) else [metadatas]

        for doc_group, metadata_group in zip(doc_groups, metadata_groups):
            for document, metadata in zip(doc_group, metadata_group):
                flattened_sources.append(
                    {
                        "content": str(document),
                        "metadata": metadata or {},
                    }
                )

    return flattened_sources[:n]

def _build_context_from_results(results: Dict[str, Any], n: int) -> str:
    """
    Safely extract documents from the query results and build a text context.
    The storage/query API may return nested lists; handle common shapes.
    """
    docs = results.get("documents", [])
    # Flatten if nested (e.g., list of lists)
    flattened: List[str] = []
    if isinstance(docs, list):
        for item in docs:
            if isinstance(item, list):
                flattened.extend(item)
            elif isinstance(item, str):
                flattened.append(item)
            else:
                # Unknown shape: try converting to str
                flattened.append(str(item))
    else:
        flattened.append(str(docs))

    if not flattened:
        return ""

    # Take up to `n` top entries
    selected = flattened[:n]
    context = "\n".join(selected)
    return context