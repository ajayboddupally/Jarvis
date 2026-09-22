from datetime import datetime, timezone

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.models import APIKey
from app.core.security import digest_api_key


async def authenticate(
    request: Request,
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> APIKey:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[7:].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    digest = digest_api_key(token, settings.api_key_pepper)
    result = await db.execute(
        select(APIKey).where(APIKey.key_digest == digest, APIKey.status == "active")
    )
    api_key = result.scalar_one_or_none()

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key.last_used_at = datetime.now(timezone.utc)
    await db.commit()
    request.state.api_key = api_key
    return api_key


async def authenticate_admin(
    x_admin_key: str | None = Header(default=None),
) -> None:
    import hmac

    if not x_admin_key or not hmac.compare_digest(x_admin_key, settings.admin_api_key):
        raise HTTPException(status_code=403, detail="Invalid administrator credentials")
