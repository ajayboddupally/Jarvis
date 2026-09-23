from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    model: str = Field(default="jarvis-local", min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=100_000)
    conversation_id: str | None = Field(default=None, max_length=120)
    temperature: float = Field(default=0.2, ge=0, le=2)
    max_tokens: int = Field(default=1024, ge=1, le=16384)
    stream: bool = False


class ChatResponse(BaseModel):
    id: str
    object: str = "response"
    model: str
    response: str
    conversation_id: str
    usage: dict[str, int]
