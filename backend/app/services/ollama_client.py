import ollama
from config.config import LLM_MODEL, EMBEDDING_MODEL, OLLAMA_HOST


_client = ollama.Client(
    host=OLLAMA_HOST,
)

def generate(prompt: str, model: str = LLM_MODEL, stream: bool = False):
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

def embed(text, model: str = EMBEDDING_MODEL):
    response = _client.embeddings(
        model=model,
        prompt=text
    )
    
    return response["embedding"]