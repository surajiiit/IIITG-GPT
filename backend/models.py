from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    id: str
    chat_id: str
    content: str
    sender: str  # 'user' or 'ai'
    timestamp: str

class Chat(BaseModel):
    id: str
    user_id: str
    created_at: str
    updated_at: str
    messages: Optional[List[Message]] = []

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    is_admin: bool = False
