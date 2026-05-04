from typing import Any, Dict, List

from chromadb import logger

from ingestion.chuncker import chunk_text
from ingestion.parser import clean_markdown
from services.ollama_client import embed

def clear_source_documents(collection: Any, knowledge_base_id: str, source_id: str) -> None:
    collection.delete(
        where={
            "$and": [
                {"knowledge_base_id": knowledge_base_id},
                {"source_id": source_id},
            ],
        }
    )


def index_documents(docs: List[Dict[str, Any]], collection: Any) -> Dict[str, int]:
    """
    Clean, chunk, embed and add documents to the collection.
    Expects docs to be a list of dicts with at least 'content' and 'path' keys.
    """
    if not docs:
        logger.warning("No documents to index.")
        return {"files_indexed": 0, "chunks_indexed": 0}

    total_chunks = 0
    total_files = 0
    for doc in docs:
        path = doc.get("path", "<unknown-path>")
        content = doc.get("content", "")
        logger.debug("Processing document: %s", path)

        try:
            cleaned = clean_markdown(content)
            chunks = chunk_text(cleaned)
        except Exception as exc:
            logger.error("Failed to clean/chunk '%s': %s", path, exc)
            continue

        indexed_chunks_for_doc = 0
        for i, chunk in enumerate(chunks):
            try:
                vector = embed(chunk)
                doc_id = ":".join(
                    [
                        str(doc.get("knowledge_base_id", "global")),
                        str(doc.get("source_id", path)),
                        path,
                        str(i),
                    ]
                )
                metadata = {
                    "knowledge_base_id": str(doc.get("knowledge_base_id", "")),
                    "source_id": str(doc.get("source_id", "")),
                    "repo_url": str(doc.get("repo_url", "")),
                    "branch": str(doc.get("branch", "")),
                    "path": path,
                    "chunk_index": i,
                }
                collection.upsert(
                    documents=[chunk],
                    embeddings=[vector],
                    ids=[doc_id],
                    metadatas=[metadata],
                )
                total_chunks += 1
                indexed_chunks_for_doc += 1
                logger.debug("Indexed chunk %s for %s", i, path)
            except Exception as exc:
                logger.exception(
                    "Failed to embed/add chunk %s for %s: %s", i, path, exc
                )

        if indexed_chunks_for_doc:
            total_files += 1

    logger.info("Indexing complete. Total chunks indexed: %d", total_chunks)
    return {"files_indexed": total_files, "chunks_indexed": total_chunks}