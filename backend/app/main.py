from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from ingestion.github_loader import ensure_deploy_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_deploy_key()
    yield


app = FastAPI(
    title="RAG API",
    description="Ollama + ChromaDB backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)

@app.get("/")
def root():
    return {"message": "API is running"}