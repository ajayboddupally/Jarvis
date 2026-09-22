from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.models import UsageRecord
from app.gateway.auth import authenticate_admin


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/usage")
async def get_usage(
    limit: int = Query(default=100, ge=1, le=1000),
    _: None = Depends(authenticate_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UsageRecord)
        .order_by(desc(UsageRecord.created_at))
        .limit(limit)
    )

    records = result.scalars().all()

    return {
        "object": "list",
        "data": [
            {
                "id": str(record.id),
                "api_key_id": str(record.api_key_id),
                "request_id": record.request_id,
                "path": record.path,
                "method": record.method,
                "model": record.model,
                "status_code": record.status_code,
                "input_tokens": record.input_tokens,
                "output_tokens": record.output_tokens,
                "latency_ms": record.latency_ms,
                "created_at": record.created_at,
            }
            for record in records
        ],
    }
