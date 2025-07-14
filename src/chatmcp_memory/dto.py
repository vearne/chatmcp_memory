from pydantic import BaseModel
from typing import List

class ChatMessage(BaseModel):
    """chat message"""
    # uuid
    message_id: str = ""
    # parent_message_id indicates which message this message is a reply to
    parent_message_id: str = ""
    # chat id
    chat_id: int = 0
    # content
    body: str = ""
    # create time
    created_at: str = ""

class Chat(BaseModel):
    """chat"""
    # chat id
    chat_id: int = 0
    # chat topic
    title: str | None = ""
    # large language models for chat
    model: str | None = ""
    # start time of conversation
    created_at: str = ""
    messages: List[ChatMessage] = []