from pydantic import BaseModel, field_validator
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


class GithubIngestRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = None      # defaults to the repo's default branch

    @field_validator("repo_url")
    @classmethod
    def must_be_github_url(cls, v: str) -> str:
        if not v.strip().startswith("https://github.com/"):
            raise ValueError("repo_url must be a https://github.com/... URL")
        return v.strip()


class GithubIngestResponse(BaseModel):
    indexed: int
    repo_url: str