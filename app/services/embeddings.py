import ollama

_client = ollama.Client(
    host="http://localhost:11434",
)

def embed(text, model="nomic-embed-text"):
    response = _client.embeddings(
        model=model,
        prompt=text
    )
    
    return response["embedding"]