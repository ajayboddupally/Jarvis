from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.models import APIKey
from app.core.security import digest_api_key, generate_api_key
from app.gateway.auth import authenticate_admin


router = APIRouter(prefix="/admin", tags=["Admin"])


class CreateAPIKeyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    owner: str = Field(min_length=1, max_length=120)


@router.post("/api-keys")
async def create_api_key(
    payload: CreateAPIKeyRequest,
    _: None = Depends(authenticate_admin),
    db: AsyncSession = Depends(get_db),
):
    raw_key = generate_api_key()

    record = APIKey(
        name=payload.name,
        owner=payload.owner,
        key_prefix=raw_key[:16],
        key_digest=digest_api_key(raw_key, settings.api_key_pepper),
        status="active",
    )

    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {
        "id": str(record.id),
        "name": record.name,
        "owner": record.owner,
        "api_key": raw_key,
        "warning": "Store this API key now. It will not be returned again.",
    }
