from fastapi import APIRouter, Depends, Request
from fastapi import HTTPException

from app.core.models import APIKey
from app.gateway.auth import authenticate
from app.gateway.rate_limit import RateLimiter


router = APIRouter(prefix="/v1", tags=["Gateway"])


@router.get("/health")
async def health():
    return {"service": "jarvis-gateway", "status": "healthy", "version": "0.1.0"}


async def enforce_rate_limit(
    request: Request,
    api_key: APIKey = Depends(authenticate),
) -> APIKey:
    limiter: RateLimiter = request.app.state.rate_limiter
    allowed, count = await limiter.check(str(api_key.id))
    request.state.rate_count = count

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": "60"},
        )

    return api_key
