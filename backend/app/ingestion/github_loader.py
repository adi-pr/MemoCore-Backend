import os

def load_markdown_files(repo_path="./data/raw"):
    """
    Loads all markdown files from a local GitHub Wiki.js backup.
    Returns list of (file_path, content).
    """
    documents = []

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".md"):
                full_path = os.path.join(root, file)

                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                documents.append({
                    "path": full_path,
                    "content": content
                })

    return documents