from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator


class QueryRequest(BaseModel):
    knowledge_base_id: str
    question: str
    top_k: Optional[int] = 4   # how many docs to retrieve


class Source(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    answer: str
    sources: Optional[List[Source]] = None


class GithubIngestRequest(BaseModel):
    branch: Optional[str] = None      # defaults to the repo's default branch
    is_private: bool = False


class KnowledgeBaseCreateRequest(BaseModel):
    giturl: str
    name: str
    description: Optional[str] = None

    @field_validator("giturl")
    @classmethod
    def must_be_github_url(cls, v: str) -> str:
        candidate = v.strip()
        if not candidate.startswith("https://github.com/"):
            raise ValueError("giturl must be a https://github.com/... URL")
        return candidate


class KnowledgeBaseResponse(BaseModel):
    id: str
    giturl: str
    name: str
    description: Optional[str] = None
    created_at: str
    updated_at: str


class GithubIngestResponse(BaseModel):
    knowledge_base_id: str
    source_id: str
    ingestion_id: str
    repo_url: str
    indexed_files: int
    indexed_chunks: int
    status: str