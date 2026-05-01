import ollama

_client = ollama.Client(
    host="http://localhost:11434",
)

def generate(prompt: str, model: str = "llama3", stream: bool = False):
    response = _client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=stream
    )

    if stream:
        for chunk in response:
            yield chunk["message"]["content"]
    else:
        return response["message"]["content"]

def embed(text, model="nomic-embed-text"):
    response = _client.embeddings(
        model=model,
        prompt=text
    )
    
    return response["embedding"]