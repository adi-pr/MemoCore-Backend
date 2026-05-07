def chunk_text(text, chunk_size=500, overlap=100):
    """
    Splits text into overlapping chunks of words while preserving single spaces.
    """
    words = text.split()
    
    # Handle edge case where text is shorter than chunk_size
    if len(words) <= chunk_size:
        return [" ".join(words)]

    chunks = []
    step = chunk_size - overlap
    
    # Ensure we don't get stuck in an infinite loop if overlap >= chunk_size
    if step <= 0:
        raise ValueError("chunk_size must be greater than overlap")

    for i in range(0, len(words), step):
        chunk = words[i : i + chunk_size]
        chunks.append(" ".join(chunk))
        
        # Stop if the current chunk reached the end of the text
        if i + chunk_size >= len(words):
            break
            
    return chunks
