import os

def load_repo(path="./data/raw"):
    files = []

    for root, _, fns in os.walk(path):
        for f in fns:
            if f.endswith(".md"):
                with open(os.path.join(root, f), "r") as file:
                    files.append(file.read())

    return files