from typing import Any, Dict, List

from chromadb import logger

from ingestion.chuncker import chunk_text
from ingestion.parser import clean_markdown
from services.embeddings import embed

def index_documents(docs: List[Dict[str, Any]], collection: Any) -> None:
    """
    Clean, chunk, embed and add documents to the collection.
    Expects docs to be a list of dicts with at least 'content' and 'path' keys.
    """
    if not docs:
        logger.warning("No documents to index.")
        return

    total_chunks = 0
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

        for i, chunk in enumerate(chunks):
            try:
                vector = embed(chunk)
                doc_id = f"{path}_{i}"
                collection.add(
                    documents=[chunk],
                    embeddings=[vector],
                    ids=[doc_id],
                )
                total_chunks += 1
                logger.debug("Indexed chunk %s for %s", i, path)
            except Exception as exc:
                logger.exception(
                    "Failed to embed/add chunk %s for %s: %s", i, path, exc
                )

    logger.info("Indexing complete. Total chunks indexed: %d", total_chunks)