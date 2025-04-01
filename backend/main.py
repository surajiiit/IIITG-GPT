# main.py
# FastAPI backend for the chatbot

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .rag_pipeline import search_pinecone
from .ollama_client import query_ollama

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def query_chatbot(request: QueryRequest):
    """Handles chatbot queries by retrieving relevant documents and generating responses."""
    try:
        relevant_docs = search_pinecone(request.query)
        response = query_ollama(request.query, relevant_docs)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "RAG Chatbot API is running!"}
