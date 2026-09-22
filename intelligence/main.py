from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from intelligence.config import settings
from intelligence.database import Base, engine, get_db
from intelligence.engine import IntelligenceEngine
from intelligence.models import ModelRouter
from intelligence.schemas import ChatRequest, ChatResponse
from intelligence.tools.registry import create_default_registry


engine_runtime = IntelligenceEngine()
model_router = ModelRouter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.service_name,
    version=settings.service_version,
    description="Jarvis model routing and inference orchestration service.",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "status": "online",
    }


@app.get("/health")
async def health():
    return {
        "service": "jarvis-intelligence",
        "status": "healthy",
    }


@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": model_router.available_models(),
    }


@app.get("/v1/tools")
async def list_tools():
    registry = create_default_registry()

    return {
        "object": "list",
        "data": [
            {
                "name": definition.name,
                "description": definition.description,
                "input_schema": definition.input_schema,
            }
            for definition in registry.definitions()
        ],
    }


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await engine_runtime.generate_response(db, payload)
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Intelligence engine failed to process the request",
        ) from exc
