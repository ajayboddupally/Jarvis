from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import UsageRecord


async def record_usage(
    db: AsyncSession,
    *,
    api_key_id,
    request_id: str,
    path: str,
    method: str,
    status_code: int,
    latency_ms: int,
    model: str | None = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
) -> None:
    db.add(
        UsageRecord(
            api_key_id=api_key_id,
            request_id=request_id,
            path=path,
            method=method,
            status_code=status_code,
            latency_ms=latency_ms,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
    )
    await db.commit()
