# MemoCore

**MemoCore** is a personal AI knowledge engine that transforms your Wiki.js content into an intelligent, searchable assistant.

It uses local embeddings and language models to let you query your own knowledge base with natural language—fully offline and private.

---

## Features

*  Semantic search over your Wiki.js markdown
*  Context-aware answers using RAG (Retrieval-Augmented Generation)
*  Fully local (powered by Ollama)
*  Fast vector search with Chroma
*  Works directly with your GitHub wiki backup

---

## Architecture

MemoCore follows a simple pipeline:

1. **Ingest**
   Pull markdown files from your Wiki.js repository

2. **Chunk**
   Split content into meaningful sections

3. **Embed**
   Convert text into vector embeddings

4. **Store**
   Save embeddings in Chroma

5. **Query**
   Retrieve relevant context and generate answers with an LLM

---

## Tech Stack

* Python
* Chroma (vector database)
* Ollama (local LLM + embeddings)
* Markdown (Wiki.js content)
