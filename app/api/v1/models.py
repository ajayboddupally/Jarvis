from fastapi import APIRouter, Depends

from app.core.models import APIKey
from app.gateway.router import enforce_rate_limit


router = APIRouter(prefix="/models", tags=["Models"])


@router.get("")
async def list_models(api_key: APIKey = Depends(enforce_rate_limit)):
    return {
        "object": "list",
        "data": [
            {
                "id": "jarvis-1",
                "object": "model",
                "owned_by": "jarvis",
                "capabilities": ["text", "reasoning", "tools"],
            }
        ],
    }
