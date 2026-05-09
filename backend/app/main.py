import secrets

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from . import models  # noqa: F401  (register models)
from .routes import analysis, auth, context, brands, tryon, sessions


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="Virtual Fashion Assistant API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(analysis.router)
    app.include_router(context.router)
    app.include_router(brands.router)
    app.include_router(tryon.router)
    app.include_router(sessions.router)

    if settings.BOOT_TOKEN_INVALIDATION:
        app.state.api_boot_id = secrets.token_hex(16)
    else:
        app.state.api_boot_id = None

    @app.get("/api/health")
    def health():
        out: dict = {"status": "ok"}
        bid = getattr(app.state, "api_boot_id", None)
        if bid:
            out["boot_id"] = bid
        return out

    return app


app = create_app()
