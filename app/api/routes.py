from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.schemas import QueryRequest, QueryResponse
from services.rag_pipeline import answer_query, answer_query_stream

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