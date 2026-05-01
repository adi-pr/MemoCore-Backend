import re

def clean_markdown(text):
    """
    Basic markdown cleanup:
    - removes excessive whitespace
    - strips weird artifacts
    - keeps content intact for embeddings
    """

    # remove multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # remove markdown links but keep text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # remove images
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

    # strip leading/trailing whitespace
    return text.strip()