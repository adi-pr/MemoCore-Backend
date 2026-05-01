from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 4   # how many docs to retrieve

class Source(BaseModel):
    content: str
    metadata: Optional[dict] = None

class QueryResponse(BaseModel):
    answer: str
    sources: Optional[List[Source]] = None