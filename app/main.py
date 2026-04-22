from ingestion.chuncker import chunk_text
from ingestion.github_loader import load_markdown_files
from ingestion.parser import clean_markdown
from core.llm import generate
from core.embedder import embed
import core.db

docs = load_markdown_files()

try:
    core.db.client.delete_collection("wiki")
except:
    pass

core.db.collection = core.db.client.get_or_create_collection("wiki")

for doc in docs:
    clean = clean_markdown(doc["content"])
    chunks = chunk_text(clean)

    for i, chunk in enumerate(chunks):
        vector = embed(chunk)

        core.db.collection.add(
            documents=[chunk],
            embeddings=[vector],
            ids=[f"{doc['path']}_{i}"]
        )

print("Wiki indexed successfully.")

def ask(question):
    q_emb = embed(question)

    results = core.db.collection.query(
        query_embeddings=[q_emb],
        n_results=2
    )

    context = "\n".join(results["documents"][0])
    
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