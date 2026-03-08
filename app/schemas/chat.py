from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class MessageItemResponse(BaseModel):
    role: str
    content: str
    created_at: datetime
