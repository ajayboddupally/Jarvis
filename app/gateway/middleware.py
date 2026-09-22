import time
import uuid

from fastapi import Request
from starlette.responses import Response

from app.core.database import SessionLocal
from app.gateway.usage import record_usage


async def request_id_middleware(request: Request, call_next) -> Response:
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()

    try:
        response = await call_next(request)
    finally:
        request.state.latency_ms = int((time.perf_counter() - started) * 1000)

        api_key = getattr(request.state, "api_key", None)

        if api_key is not None:
            try:
                async with SessionLocal() as db:
                    await record_usage(
                        db,
                        api_key_id=api_key.id,
                        request_id=request_id,
                        path=request.url.path,
                        method=request.method,
                        status_code=getattr(response, "status_code", 500),
                        latency_ms=request.state.latency_ms,
                        model=getattr(request.state, "model", None),
                        input_tokens=getattr(request.state, "input_tokens", 0),
                        output_tokens=getattr(request.state, "output_tokens", 0),
                    )
            except Exception:
                # Usage recording must never take down an otherwise successful request.
                pass

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
