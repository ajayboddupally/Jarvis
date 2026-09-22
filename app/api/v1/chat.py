from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.models import APIKey
from app.core.service_client import ServiceUnavailableError, forward_to_intelligence
from app.gateway.router import enforce_rate_limit


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    model: str = Field(default="jarvis-1", min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=100_000)
    stream: bool = False


class ChatResponse(BaseModel):
    id: str
    object: str
    model: str
    response: str
    request_id: str


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    request: Request,
    api_key: APIKey = Depends(enforce_rate_limit),
):
    del api_key

    try:
        result = await forward_to_intelligence(payload.model_dump())
    except ServiceUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ChatResponse(
        id=result.get("id", f"resp_{uuid4().hex}"),
        object=result.get("object", "response"),
        model=result.get("model", payload.model),
        response=result.get("response", result.get("output_text", "")),
        request_id=request.state.request_id,
    )
