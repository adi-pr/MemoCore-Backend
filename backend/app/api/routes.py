from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.schemas import QueryRequest, QueryResponse
from ingestion.idexer import index_documents
from ingestion.github_loader import load_markdown_files
from services.rag_pipeline import answer_query, answer_query_stream

from db.chroma_client import collection

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

@router.get("/index")
def index():
    try:
        docs = load_markdown_files()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if docs:
        index_documents(docs, collection)
        return {"message": f"Indexed {len(docs)} documents"}
    else:
        return {"message": "No documents found to index"}