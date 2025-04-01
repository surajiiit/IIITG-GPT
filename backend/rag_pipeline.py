# rag_pipeline.py
# Handles embedding generation and retrieval from Pinecone

import torch
from pinecone import Pinecone
from transformers import AutoModel, AutoTokenizer
from .config import PINECONE_API_KEY, INDEX_NAME, EMBEDDING_MODEL, DEVICE

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# Load Embedding Model
tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL, trust_remote_code=True)
model = AutoModel.from_pretrained(EMBEDDING_MODEL, trust_remote_code=True).to(DEVICE)
model.eval()

def generate_embedding(text):
    """Generates an embedding for a given text."""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(DEVICE)
    with torch.no_grad():
        embedding = model(**inputs).last_hidden_state.mean(dim=1).cpu().numpy().flatten()
    return embedding.tolist()

def search_pinecone(query, top_k=5):
    """Retrieves top K relevant documents from Pinecone using query embeddings."""
    query_embedding = generate_embedding(query)
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    relevant_docs = "\n".join([match["metadata"].get("text", "") for match in results.get("matches", [])])
    return relevant_docs
