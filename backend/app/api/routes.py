from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.schemas import GithubIngestRequest, GithubIngestResponse, QueryRequest, QueryResponse
from ingestion.idexer import index_documents
from ingestion.github_loader import load_from_github, _DEFAULT_KEY_PATH
from services.rag_pipeline import answer_query, answer_query_stream

from db.chroma_client import collection
import os

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/ask", response_model=QueryResponse)
async def ask(query: QueryRequest):
    try:
        result = answer_query(
            question=query.question,
            top_k=query.top_k
        )

        return QueryResponse(
            answer=result["answer"],
            sources=result.get("sources")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/ask/stream")
def ask_stream(payload: QueryRequest):
    
    return StreamingResponse(
        answer_query_stream(payload.question, payload.top_k),
        media_type="text/plain"
    )

@router.post("/ingest/github", response_model=GithubIngestResponse)
def ingest_github(payload: GithubIngestRequest):
    try:
        docs = load_from_github(
            repo_url=payload.repo_url,
            branch=payload.branch,
        )
    except ValueError as e:
        pub_key_path = os.getenv("GITHUB_DEPLOY_KEY_PATH", _DEFAULT_KEY_PATH) + ".pub"
        try:
            pub_key = open(pub_key_path).read().strip()
            hint = f" If this is a private repo, add this deploy key to it (Settings → Deploy keys): {pub_key}"
        except OSError:
            hint = ""
        raise HTTPException(status_code=422, detail=f"{e}{hint}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if docs:
        index_documents(docs, collection)

    return GithubIngestResponse(indexed=len(docs), repo_url=payload.repo_url)