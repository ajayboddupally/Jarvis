import time
import uuid

from fastapi import Request
from starlette.responses import Response


async def request_id_middleware(request: Request, call_next) -> Response:
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()

    try:
        response = await call_next(request)
    finally:
        request.state.latency_ms = int((time.perf_counter() - started) * 1000)

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Jarvis-Gateway"] = "jarvis"
    return response


async def body_size_limit_middleware(request: Request, call_next) -> Response:
    content_length = request.headers.get("content-length")

    if content_length:
        from app.core.config import settings

        if int(content_length) > settings.max_request_body_bytes:
            from fastapi import HTTPException
            raise HTTPException(status_code=413, detail="Request body is too large")

    return await call_next(request)
