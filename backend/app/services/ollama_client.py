import ollama
from config.config import LLM_MODEL, EMBEDDING_MODEL, OLLAMA_HOST

import time


_client = ollama.Client(
    host=OLLAMA_HOST,
)

def generate(prompt: str, model: str = LLM_MODEL, stream: bool = False):

    t0 = time.time()

    print("Promt size:", len(prompt))
    
    response = _client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=stream
    )

    print("Prompt sent to Ollama:", prompt)

    if stream:
        for chunk in response:
            yield chunk["message"]["content"]
    else:
        return response["message"]["content"]

    t1 = time.time()
    print(f"Ollama response time: {t1 - t0:.2f} seconds")

def embed(text, model: str = EMBEDDING_MODEL):
    t0 = time.time()

    response = _client.embeddings(
        model=model,
        prompt=text
    )

    t1 = time.time()
    print(f"Ollama embedding response time: {t1 - t0:.2f} seconds")
    
    return response["embedding"]