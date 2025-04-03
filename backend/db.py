"""
In-memory database module for MVP version.
This would be replaced with a proper database in production.
"""

from models import Chat, Message, User
from typing import List, Dict, Optional

# In-memory database
chats_db: Dict[str, dict] = {}
messages_db: Dict[str, List[dict]] = {}
users_db: Dict[str, dict] = {}

# Default admin user (in real world, this would be in a secure database)
default_admin = User(
    username="admin",
    email="admin@example.com",
    full_name="Admin User",
    disabled=False,
    is_admin=True,
)
users_db["admin"] = {
    "username": default_admin.username,
    "email": default_admin.email,
    "full_name": default_admin.full_name,
    "disabled": default_admin.disabled,
    "is_admin": default_admin.is_admin,
    # In a real app, this would be properly hashed
    "hashed_password": "$2b$12$5nU0TVAXHn1hhuTQ8NpIyuVdz7hFcGNqm5Qgbe.9USbgMHdLpwU6m"  # "password123"
}

# Chat operations
def add_chat(chat: Chat) -> None:
    chats_db[chat.id] = {
        "id": chat.id,
        "user_id": chat.user_id,
        "created_at": chat.created_at,
        "updated_at": chat.updated_at,
    }
    messages_db[chat.id] = []

def get_chat(chat_id: str) -> Optional[dict]:
    return chats_db.get(chat_id)

def get_chats() -> List[dict]:
    chat_list = []
    for chat_id, chat in chats_db.items():
        chat_with_messages = {**chat, "messages": get_messages_by_chat_id(chat_id)}
        chat_list.append(chat_with_messages)
    return chat_list

# Message operations
def add_message(message: Message) -> None:
    if message.chat_id not in messages_db:
        messages_db[message.chat_id] = []
    
    message_dict = {
        "id": message.id,
        "chat_id": message.chat_id,
        "content": message.content,
        "sender": message.sender,
        "timestamp": message.timestamp
    }
    
    messages_db[message.chat_id].append(message_dict)

def get_messages_by_chat_id(chat_id: str) -> List[dict]:
    return messages_db.get(chat_id, [])

# User operations
def get_user(username: str) -> Optional[User]:
    user_data = users_db.get(username)
    if not user_data:
        return None
    return User(**user_data)

def get_user_with_password(username: str) -> Optional[dict]:
    return users_db.get(username)
