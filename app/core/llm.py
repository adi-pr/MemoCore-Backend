import ollama

client = ollama.Client(
    host="http://localhost:11434",
)

def generate(prompt, model="llama3"):
    response = client.chat(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"]