from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.schemas import (
    GithubIngestRequest,
    GithubIngestResponse,
    KnowledgeBaseCreateRequest,
    KnowledgeBaseResponse,
    KnowledgeBaseSourceResponse,
    QueryRequest,
    QueryResponse,
)
from db.catalog import (
    complete_ingestion,
    create_github_source,
    create_ingestion,
    create_knowledge_base,
    fail_ingestion,
    get_knowledge_base,
    list_knowledge_bases,
    list_sources,
)
from services.rag_pipeline import answer_query, answer_query_stream
from ingestion.github_loader import get_public_deploy_key, load_from_github
from ingestion.idexer import clear_source_documents, index_documents

from db.chroma_client import collection

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/ask", response_model=QueryResponse)
async def ask(query: QueryRequest):
    if get_knowledge_base(query.knowledge_base_id) is None:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    try:
        result = answer_query(
            question=query.question,
            knowledge_base_id=query.knowledge_base_id,
            n_results=query.top_k,
        )

        return QueryResponse(
            answer=result["answer"],
            sources=result.get("sources")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/ask/stream")
def ask_stream(payload: QueryRequest):
    if get_knowledge_base(payload.knowledge_base_id) is None:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    return StreamingResponse(
        answer_query_stream(payload.question, payload.knowledge_base_id, payload.top_k),
        media_type="text/plain"
    )


def _require_knowledge_base(knowledge_base_id: str):
    knowledge_base = get_knowledge_base(knowledge_base_id)
    if knowledge_base is None:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return knowledge_base


def _private_repo_hint() -> str:
    try:
        public_key = get_public_deploy_key()
    except OSError:
        return ""

    return (
        " If this is a private repo, add this deploy key to the repository "
        f"(Settings -> Deploy keys): {public_key}"
    )


def _github_access_hint(error_message: str, is_private: bool) -> str:
    if not is_private:
        return ""

    access_error_markers = (
        "git clone failed",
        "permission denied",
        "repository not found",
        "could not read from remote repository",
    )
    lowered = error_message.lower()
    if any(marker in lowered for marker in access_error_markers):
        return _private_repo_hint()

    return ""


@router.post("/knowledge-bases", response_model=KnowledgeBaseResponse)
def create_knowledge_base_route(payload: KnowledgeBaseCreateRequest):
    knowledge_base = create_knowledge_base(payload.name, payload.description)
    return KnowledgeBaseResponse(**knowledge_base)


@router.get("/knowledge-bases", response_model=List[KnowledgeBaseResponse])
def list_knowledge_bases_route():
    return [KnowledgeBaseResponse(**item) for item in list_knowledge_bases()]


@router.get("/knowledge-bases/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
def get_knowledge_base_route(knowledge_base_id: str):
    knowledge_base = _require_knowledge_base(knowledge_base_id)
    return KnowledgeBaseResponse(**knowledge_base)


@router.get(
    "/knowledge-bases/{knowledge_base_id}/sources",
    response_model=List[KnowledgeBaseSourceResponse],
)
def list_knowledge_base_sources(knowledge_base_id: str):
    _require_knowledge_base(knowledge_base_id)
    return [KnowledgeBaseSourceResponse(**item) for item in list_sources(knowledge_base_id)]


@router.post(
    "/knowledge-bases/{knowledge_base_id}/sources/github",
    response_model=GithubIngestResponse,
)
def ingest_github(knowledge_base_id: str, payload: GithubIngestRequest):
    _require_knowledge_base(knowledge_base_id)

    source = create_github_source(
        knowledge_base_id=knowledge_base_id,
        repo_url=payload.repo_url,
        branch=payload.branch,
        is_private=payload.is_private,
    )
    ingestion = create_ingestion(knowledge_base_id, source["id"])

    try:
        docs = load_from_github(repo_url=payload.repo_url, branch=payload.branch)
        clear_source_documents(collection, knowledge_base_id, source["id"])
        indexed = index_documents(
            [
                {
                    **document,
                    "knowledge_base_id": knowledge_base_id,
                    "source_id": source["id"],
                    "repo_url": payload.repo_url,
                    "branch": payload.branch or "",
                }
                for document in docs
            ],
            collection,
        )
        complete_ingestion(
            ingestion["id"],
            source["id"],
            files_seen=len(docs),
            files_indexed=indexed["files_indexed"],
            chunks_indexed=indexed["chunks_indexed"],
        )
    except ValueError as exc:
        fail_ingestion(ingestion["id"], source["id"], str(exc))
        raise HTTPException(
            status_code=422,
            detail=f"{exc}{_github_access_hint(str(exc), payload.is_private)}",
        )
    except Exception as exc:
        fail_ingestion(ingestion["id"], source["id"], str(exc))
        raise HTTPException(status_code=500, detail=str(exc))

    return GithubIngestResponse(
        knowledge_base_id=knowledge_base_id,
        source_id=source["id"],
        ingestion_id=ingestion["id"],
        repo_url=payload.repo_url,
        indexed_files=indexed["files_indexed"],
        indexed_chunks=indexed["chunks_indexed"],
        status="completed",
    )