import logging
from typing import List, Dict, Any, Optional
import torch
import requests
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from config import EMBEDDING_MODEL, OLLAMA_URL, PINECONE_API_KEY, INDEX_NAME

# ----- SETUP LOGGING -----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ----- CONSTANTS -----
SYSTEM_PROMPT = (
    "You are a helpful assistant for IIIT Guwahati. Answer questions accurately using only the provided information. "
    "If you don't have relevant information, simply state that you don't know. "
    "Be concise, helpful, and professional."
)

# ----- DEVICE CONFIGURATION -----
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {DEVICE}")

# ----- GLOBAL RESOURCES -----
try:
    MODEL = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True).to(DEVICE)
    MODEL.eval()
    logger.info(f"Successfully loaded embedding model: {EMBEDDING_MODEL}")
except Exception as e:
    logger.error(f"Failed to initialize embedding model: {str(e)}")
    raise RuntimeError(f"Model initialization failed: {str(e)}")

try:
    PC = Pinecone(api_key=PINECONE_API_KEY)
    INDEX = PC.Index(INDEX_NAME)
    logger.info(f"Successfully connected to Pinecone index: {INDEX_NAME}")
except Exception as e:
    logger.error(f"Failed to initialize Pinecone: {str(e)}")
    raise RuntimeError(f"Pinecone initialization failed: {str(e)}")

# ----- FUNCTIONS -----
def generate_embedding(query: str) -> List[float]:
    """
    Generate embeddings for the given query using the SentenceTransformer model.

    Args:
        query (str): The input query string to embed.

    Returns:
        List[float]: Normalized embedding vector as a list for Pinecone compatibility.

    Raises:
        RuntimeError: If embedding generation fails.
    """
    try:
        logger.debug(f"Generating embedding for query: {query[:50]}...")
        with torch.no_grad():
            embedding = MODEL.encode(query, convert_to_tensor=True).cpu()
        return embedding.numpy().flatten().tolist()
    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        raise RuntimeError(f"Failed to generate embedding: {str(e)}")

def search_pinecone(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Search Pinecone for the top K relevant documents based on the query embedding.

    Args:
        query (str): The query string to search for.
        top_k (int): Number of top results to retrieve (default: 5).

    Returns:
        Dict[str, Any]: Pinecone query results containing matches, or empty matches if none found.

    Raises:
        RuntimeError: If the search operation fails.
    """
    try:
        query_embedding = generate_embedding(query)
        results = INDEX.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        return results if results.get("matches") else {"matches": []}
    except Exception as e:
        logger.error(f"Pinecone search failed: {str(e)}")
        raise RuntimeError(f"Pinecone search failed: {str(e)}")

def query_llama(query: str, top_k: int = 5) -> str:
    """
    Query Llama with retrieved documents from Pinecone using the RAG pipeline.

    Args:
        query (str): The user query to process.
        top_k (int): Number of top documents to retrieve (default: 5).

    Returns:
        str: Response from Llama or an error message.

    Raises:
        RuntimeError: If the Llama API call or query processing fails.
    """
    try:
        logger.info(f"Processing RAG query: {query[:50]}...")
        search_results = search_pinecone(query, top_k)
        relevant_docs = "\n".join(
            [match["metadata"].get("text", "") for match in search_results.get("matches", [])]
        ) or "No relevant information found."

        full_prompt = f"{SYSTEM_PROMPT}\n\nRelevant Information:\n{relevant_docs}\n\nQuery: {query}"
        payload = {
            "model": "llama3.2",
            "prompt": full_prompt,
            "stream": False
        }

        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        return response.json().get("response", "No response received")
    except requests.exceptions.RequestException as e:
        logger.error(f"Llama API request failed: {str(e)}")
        raise RuntimeError(f"Llama API error: {str(e)}")
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        raise RuntimeError(f"Query processing failed: {str(e)}")