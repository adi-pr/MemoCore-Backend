def chunk_text(text, chunk_size=500, overlap=100):
    """
    Splits text into overlapping chunks.
    This improves retrieval quality in vector search.
    """

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = words[start:end]

        chunks.append(" ".join(chunk))

        start += chunk_size - overlap

    return chunks