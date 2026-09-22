import httpx

from app.core.config import settings


class ServiceUnavailableError(RuntimeError):
    pass


async def forward_to_intelligence(payload: dict) -> dict:
    url = f"{settings.intelligence_service_url.rstrip('/')}/v1/chat"

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise ServiceUnavailableError("Jarvis Intelligence Service is unavailable") from exc
