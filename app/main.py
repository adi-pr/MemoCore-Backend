import logging
import sys
from typing import Any, Dict, List, Optional

import core.db
from core.embedder import embed
from core.llm import generate
from ingestion.chuncker import chunk_text
from ingestion.github_loader import load_markdown_files
from ingestion.parser import clean_markdown

# Constants
COLLECTION_NAME = "wiki"
N_RESULTS = 2  # number of context chunks to retrieve for a query
DEBUG = False

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("memo-core")


def prepare_collection(name: str) -> Any:
    """
    Ensure the target collection is fresh and available.
    If a collection with the same name exists, try to delete it first.
    Returns the collection object.
    """
    client = core.db.client
    try:
        logger.info("Deleting existing collection '%s' (if present)...", name)
        client.delete_collection(name)
    except Exception as exc:
        # It's fine if the collection did not exist; log for diagnostics.
        logger.debug("delete_collection raised: %s", exc)
    collection = client.get_or_create_collection(name)
    core.db.collection = collection
    logger.info("Collection '%s' is ready.", name)
    return collection


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


def ask(question: str, collection: Any, n_results: int = N_RESULTS) -> str:
    """
    Embed the question, query the collection for relevant context, and ask the LLM.
    Returns the LLM-generated response text.
    """
    if not question.strip():
        return "Please provide a non-empty question."

    try:
        q_emb = embed(question)
    except Exception as exc:
        logger.exception("Failed to embed question: %s", exc)
        return "Error: failed to embed the question."

    try:
        results = collection.query(
            query_embeddings=[q_emb],
            n_results=n_results,
        )
    except Exception as exc:
        logger.exception("Query failed: %s", exc)
        return "Error: query failed."

    context = _build_context_from_results(results, n_results)
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
        return "Error: failed to generate a response."

    return response


def interactive_loop(collection: Any) -> None:
    """
    Simple REPL for asking questions to the indexed wiki.
    Commands:
      - 'exit' or 'quit' to leave
      - empty input is ignored
    """
    logger.info("Entering interactive mode. Type 'exit' or 'quit' to stop.")
    try:
        while True:
            try:
                q = input("\nAsk MemoCore: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()  # newline on ctrl-c / ctrl-d
                logger.info("Exiting interactive mode.")
                break

            if not q:
                continue
            if q.lower() in {"exit", "quit"}:
                logger.info("User requested exit.")
                break

            print("\nThinking...\n")
            answer = ask(q, collection)
            print(answer)
    except Exception as exc:
        logger.exception("Unexpected error in interactive loop: %s", exc)


def main(index_only: Optional[bool] = False) -> None:
    """
    Main entrypoint:
    - Load docs
    - Prepare collection
    - Index docs
    - Enter interactive loop (unless index_only is True)
    """
    logger.info("Starting memo-core main script.")
    docs = []
    try:
        docs = load_markdown_files()
        logger.info("Loaded %d markdown documents.", len(docs))
    except Exception as exc:
        logger.exception("Failed to load markdown files: %s", exc)
        # We continue: maybe the user still wants to interact with an existing index.

    collection = prepare_collection(COLLECTION_NAME)

    if docs:
        index_documents(docs, collection)
        logger.info("Wiki indexed successfully.")
    else:
        logger.warning("No documents were indexed.")

    if not index_only:
        interactive_loop(collection)
    else:
        logger.info("Index-only mode: exiting after indexing.")


if __name__ == "__main__":
    # Simple CLI: if an argument is provided and equals '--index-only' we skip the REPL.
    index_only_flag = "--index-only" in sys.argv[1:]
    main(index_only=index_only_flag)
