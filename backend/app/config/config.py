import os 
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", 8000))

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
LLM_MODEL = os.getenv("LLM_MODEL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

GITHUB_DEPLOY_KEY_PATH = os.getenv("GITHUB_DEPLOY_KEY_PATH")  # path to SSH deploy key private key file
CATALOG_DB_PATH = os.getenv("CATALOG_DB_PATH", "./data/catalog.db")