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
