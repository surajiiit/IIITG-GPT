from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
import httpx
import uuid
from datetime import datetime, timedelta
import json
import os

# Use absolute imports instead of relative
from models import Chat, Message, User
from db import get_chats, add_chat, get_chat, add_message, get_messages_by_chat_id
from auth import get_current_admin_user, authenticate_user, create_access_token, Token
from rag_pipeline import query_llama

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama API URL - Change this to your actual Ollama server URL
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
MODEL_NAME = "llama3.2"  # Using Llama 3.2 model


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# API Models
class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class ChatHistory(BaseModel):
    chat_id: str
    messages: List[dict]
    created_at: str
    updated_at: str

class ChatFilter(BaseModel):
    user_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

# Routes
@app.post("/api/token", response_model=Token)
async def login_for_access_token(login_data: AdminLoginRequest):
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/admin/chats", response_model=List[dict])
async def get_all_chats(current_user: User = Depends(get_current_admin_user)):
    """Get all chat histories for admin dashboard"""
    chats = get_chats()
    return chats

@app.post("/api/admin/chats/filter", response_model=List[dict])
async def filter_chats(
    filter_params: ChatFilter,
    current_user: User = Depends(get_current_admin_user)
):
    """Filter chat histories by user_id and/or date range"""
    chats = get_chats()
    filtered_chats = []
    
    for chat in chats:
        # Filter by user_id
        if filter_params.user_id and chat["user_id"] != filter_params.user_id:
            continue
            
        # Filter by date range
        if filter_params.start_date:
            chat_date = datetime.fromisoformat(chat["created_at"])
            start_date = datetime.fromisoformat(filter_params.start_date)
            if chat_date < start_date:
                continue
                
        if filter_params.end_date:
            chat_date = datetime.fromisoformat(chat["created_at"])
            end_date = datetime.fromisoformat(filter_params.end_date)
            if chat_date > end_date:
                continue
                
        filtered_chats.append(chat)
        
    return filtered_chats

@app.get("/api/admin/chats/{chat_id}", response_model=dict)
async def get_chat_history(
    chat_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific chat history by ID"""
    chat = get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@app.post("/api/admin/export", response_model=dict)
async def export_chats(
    filter_params: Optional[ChatFilter] = None,
    format: str = "json",
    current_user: User = Depends(get_current_admin_user)
):
    """Export chat histories in JSON or CSV format"""
    # Get chats (filtered if parameters provided)
    if filter_params:
        chats = await filter_chats(filter_params, current_user)
    else:
        chats = get_chats()
    
    if format.lower() == "json":
        return {"data": chats, "format": "json"}
    elif format.lower() == "csv":
        # Convert to CSV format (just sending the data that would be converted)
        return {"data": chats, "format": "csv"}
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

@app.post("/api/chat", response_model=dict)
async def create_chat(user_data: ChatMessage):
    """Create a new chat session"""
    user_id = user_data.user_id or str(uuid.uuid4())
    chat_id = str(uuid.uuid4())
    
    # Create chat in database
    chat = Chat(
        id=chat_id,
        user_id=user_id,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    add_chat(chat)
    
    return {"chat_id": chat_id, "user_id": user_id}

@app.post("/api/chat/{chat_id}/message", response_model=dict)
async def send_message(chat_id: str, message_data: ChatMessage):
    """Send a message to the chatbot and get AI response"""
    # Validate chat exists
    chat = get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Save user message
    user_message = Message(
        id=str(uuid.uuid4()),
        chat_id=chat_id,
        content=message_data.message,
        sender="user",
        timestamp=datetime.now().isoformat()
    )
    add_message(user_message)
    
    # Generate AI response using Ollama
    try:
        # Use the RAG pipeline for all queries
        ai_response_text = query_llama(message_data.message)
        print(f"Generated response via RAG pipeline: {ai_response_text[:50]}...")
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while generating a response")
    
    # Save AI response
    ai_message = Message(
        id=str(uuid.uuid4()),
        chat_id=chat_id,
        content=ai_response_text,
        sender="ai",
        timestamp=datetime.now().isoformat()
    )
    add_message(ai_message)
    
    # Update chat last activity
    chat["updated_at"] = datetime.now().isoformat()
    
    return {
        "message": ai_response_text,
        "chat_id": chat_id
    }

@app.get("/api/chat/{chat_id}", response_model=dict)
async def get_chat_messages(chat_id: str):
    """Get all messages in a chat session"""
    chat = get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = get_messages_by_chat_id(chat_id)
    
    return {
        "chat_id": chat_id,
        "user_id": chat["user_id"],
        "messages": messages,
        "created_at": chat["created_at"],
        "updated_at": chat["updated_at"]
    }

# RAG Query Endpoint
@app.post("/api/query")
async def query(query_request: ChatMessage):
    """Process a query through the RAG pipeline"""
    try:
        # Use RAG pipeline directly to fetch response
        response = query_llama(query_request.message)
        return {"response": response}
    except Exception as e:
        print(f"Error in RAG pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process query via RAG pipeline")

# For testing and development
@app.get("/")
async def root():
    return {"message": "AI Chatbot API is running"}
