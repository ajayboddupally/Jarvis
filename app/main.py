from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from app.api.v1.admin import router as admin_router
from app.api.v1.chat import router as chat_router
from app.api.v1.models import router as models_router
from app.core.config import settings
from app.core.database import Base, engine
from app.gateway.middleware import body_size_limit_middleware, request_id_middleware
from app.gateway.rate_limit import RateLimiter
from app.gateway.router import router as gateway_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    await redis.ping()

    app.state.redis = redis
    app.state.rate_limiter = RateLimiter(redis)

    yield

    await redis.aclose()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API Gateway for the Jarvis Intelligence platform.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.middleware("http")(request_id_middleware)
app.middleware("http")(body_size_limit_middleware)

app.include_router(gateway_router)
app.include_router(chat_router, prefix="/v1")
app.include_router(models_router, prefix="/v1")
app.include_router(admin_router, prefix="/v1")


@app.get("/")
async def root():
    return {
        "name": "Jarvis Intelligence",
        "service": "API Gateway",
        "version": "0.1.0",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"service": "jarvis-gateway", "status": "healthy"}
