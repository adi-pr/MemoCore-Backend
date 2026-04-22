import ollama

client = ollama.Client(
    host="http://localhost:11434",
)

def embed(text, model="nomic-embed-text"):
    response = client.embeddings(
        model=model,
        prompt=text
    )
    
    return response["embedding"]