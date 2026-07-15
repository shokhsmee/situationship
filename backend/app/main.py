"""FastAPI application factory. Wiring only — no business logic lives here."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.redis import redis_client
from app.ws.game_socket import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail fast if Redis is unreachable at boot in non-debug environments.
    try:
        await redis_client.ping()
    except Exception:  # pragma: no cover - depends on infra
        if not settings.debug:
            raise
    yield
    await redis_client.aclose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.include_router(ws_router)

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "app": settings.app_name}

    return app


app = create_app()
