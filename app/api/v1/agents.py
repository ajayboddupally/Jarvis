from fastapi import APIRouter, Depends

from app.core.models import APIKey
from app.gateway.router import enforce_rate_limit


router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("")
async def list_agents(api_key: APIKey = Depends(enforce_rate_limit)):
    return {
        "object": "list",
        "data": [
            {
                "id": "jarvis-agent-1",
                "object": "agent",
                "status": "planned",
                "capabilities": ["reasoning", "tools", "memory"],
            }
        ],
    }
