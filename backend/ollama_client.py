# ollama_client.py
# Handles interaction with Ollama for text generation

import requests
from .config import OLLAMA_URL, SYSTEM_PROMPT

def query_ollama(query, relevant_docs):
    """Queries Ollama with retrieved documents."""
    full_prompt = f"{SYSTEM_PROMPT}\n\nRelevant Information:\n{relevant_docs}\n\nQuery: {query}"
    
    payload = {
        "model": "llama3.2",
        "prompt": full_prompt,
        "stream": False
    }
    
    response = requests.post(OLLAMA_URL, json=payload)
    
    if response.status_code == 200:
        return response.json().get("response", "No response received")
    else:
        return f"Error: {response.status_code} - {response.text}"
