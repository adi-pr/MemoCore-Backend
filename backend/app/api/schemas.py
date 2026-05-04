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
    repo_url: str
    branch: Optional[str] = None      # defaults to the repo's default branch
    is_private: bool = False

    @field_validator("repo_url")
    @classmethod
    def must_be_github_url(cls, v: str) -> str:
        if not v.strip().startswith("https://github.com/"):
            raise ValueError("repo_url must be a https://github.com/... URL")
        return v.strip()


class KnowledgeBaseCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: str
    updated_at: str


class KnowledgeBaseSourceResponse(BaseModel):
    id: str
    knowledge_base_id: str
    source_type: str
    repo_url: Optional[str] = None
    branch: Optional[str] = None
    path_prefix: Optional[str] = None
    is_private: bool
    status: str
    last_indexed_at: Optional[str] = None
    error_message: Optional[str] = None
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