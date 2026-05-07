from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.schemas import (
    KnowledgeBaseCreateRequest,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdateRequest,
    QueryRequest,
    QueryResponse,
)
from db.catalog import (
    create_knowledge_base,
    delete_knowledge_base,
    get_knowledge_base,
    list_knowledge_bases,
    update_knowledge_base,
)
from services.rag_pipeline import answer_query, answer_query_stream

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


@router.post("/knowledge-bases", response_model=KnowledgeBaseResponse)
def create_knowledge_base_route(payload: KnowledgeBaseCreateRequest):
    knowledge_base = create_knowledge_base(payload.giturl, payload.name, payload.description)
    return KnowledgeBaseResponse(**knowledge_base)


@router.get("/knowledge-bases", response_model=List[KnowledgeBaseResponse])
def list_knowledge_bases_route():
    return [KnowledgeBaseResponse(**item) for item in list_knowledge_bases()]


@router.get("/knowledge-bases/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
def get_knowledge_base_route(knowledge_base_id: str):
    knowledge_base = _require_knowledge_base(knowledge_base_id)
    return KnowledgeBaseResponse(**knowledge_base)


@router.put("/knowledge-bases/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
def update_knowledge_base_route(knowledge_base_id: str, payload: KnowledgeBaseUpdateRequest):
    if payload.giturl is None and payload.name is None and payload.description is None:
        raise HTTPException(status_code=400, detail="At least one field is required")

    knowledge_base = update_knowledge_base(
        knowledge_base_id,
        giturl=payload.giturl,
        name=payload.name,
        description=payload.description,
    )
    if knowledge_base is None:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return KnowledgeBaseResponse(**knowledge_base)


@router.delete("/knowledge-bases/{knowledge_base_id}", status_code=204)
def delete_knowledge_base_route(knowledge_base_id: str):
    if not delete_knowledge_base(knowledge_base_id):
        raise HTTPException(status_code=404, detail="Knowledge base not found")