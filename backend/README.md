# Memo Core Backend

FastAPI backend for a local RAG (Retrieval-Augmented Generation) stack using:

- Ollama for embeddings and chat generation
- ChromaDB for vector storage and retrieval
- Markdown files as the source knowledge base

## Project Structure

```
backend/
	app/
		main.py
		api/
		db/
		ingestion/
		services/
	data/
		raw/
		chroma/
	docker/
		docker-compose.yml
	requirements.txt
```

## Requirements

- Python 3.10+
- Ollama running locally on `http://localhost:11434`
- ChromaDB (local persistent mode or Docker service)

Install Python dependencies:

```bash
cd backend
pip install -r requirements.txt
```

## Run Infrastructure (Optional via Docker)

From the backend folder:

```bash
docker compose -f docker/docker-compose.yml up -d
```

This starts:

- Ollama on port `11434`

## Run the API

From the backend folder:

```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

## Data and Indexing

- Source markdown files are read from `./data/raw` (relative to `backend/app` when running).
- Vector data is persisted in `../data/chroma`.

Index markdown documents:

```bash
curl http://localhost:8080/index
```

## API Endpoints

- `GET /` - basic service status
- `GET /health` - health check
- `GET /index` - load markdown files and index them into ChromaDB
- `POST /ask` - query the RAG pipeline and return JSON response
- `POST /ask/stream` - query the RAG pipeline with streaming text response

### `POST /ask/stream` example

```bash
curl -N -X POST http://localhost:8080/ask/stream \
	-H "Content-Type: application/json" \
	-d '{"question":"Summarize my network setup","top_k":4}'
```

## Notes

- Default Ollama model in code: `llama3`
- Default embedding model in code: `nomic-embed-text`
- CORS is currently open (`allow_origins=["*"]`) and should be restricted for production.
