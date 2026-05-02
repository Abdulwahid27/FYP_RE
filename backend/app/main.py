from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import Base, engine
from . import models  # noqa: F401  (register models)
from .routes import analysis, context, brands, tryon, sessions


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

    app.mount(
        "/uploads",
        StaticFiles(directory=str(settings.UPLOAD_DIR)),
        name="uploads",
    )

    app.include_router(analysis.router)
    app.include_router(context.router)
    app.include_router(brands.router)
    app.include_router(tryon.router)
    app.include_router(sessions.router)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
