# __init__.py
# Marks the backend as a package and initializes components

import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

# Configuration Variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "your_pinecone_api_key")
INDEX_NAME = os.getenv("INDEX_NAME", "your_index_name")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-ai/nomic-embed-text-v2-moe")
