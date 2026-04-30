import ollama

client = ollama.Client(
    host="http://localhost:11434",
)

def generate_stream(prompt: str, model: str = "llama3"):
    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    for chunk in response:
        yield chunk["message"]["content"]


def generate(prompt: str, model: str = "llama3") -> str:
    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )
    return response["message"]["content"]