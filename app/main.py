from core.llm import generate
from core.embedder import embed
import core.db

notes = [
    "Docker is a containerization platform that allows you to package applications and their dependencies into portable containers.",
    "Chroma is a vector database used for semantic search.",
    "Ollama is a tool that lets you run large language models locally on your machine. It enables running models like Llama 3 without cloud APIs."
]

core.db.client.delete_collection("wiki")
core.db.collection = core.db.client.create_collection("wiki")

for i, note in enumerate(notes):
    print(f"Adding note {i}: {note}")
    core.db.collection.add(
        documents=[note],
        embeddings=[embed(note)],
        ids=[f"note-{i}"]
    )

print("Indexed test notes.")

def ask(question):
    q_emb = embed(question)

    results = core.db.collection.query(
        query_embeddings=[q_emb],
        n_results=2
    )

    context = "\n".join(results["documents"][0])
    
    print("RESULTS:", results["documents"])

    response = generate(
        prompt=f"""
Use the context to answer the question.

Context:
{context}

Question:
{question}
"""
    )

    return response
    
while True:
    q = input("\nAsk MemoCore: ")
    
    
    print("\n", ask(q))