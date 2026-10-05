from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    conversation_id: int | None = None
    chatbot_type: Literal["engineer", "doctor", "lawyer"]


class ChatResponse(BaseModel):
    error: bool = False
    conversation_id: int
    chatbot_type: str
    response: str


class ConversationSummary(BaseModel):
    id: int
    chatbot_type: str
    title: str
    updated_at: datetime


class ConversationDetail(ConversationSummary):
    messages: list["ConversationMessage"]


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
