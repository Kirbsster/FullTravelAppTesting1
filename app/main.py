from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .settings import settings
from .database import init_db
from .routers import auth, index

def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=(settings.env.lower()=="dev"))

    # CORS – adjust origins for your frontend later
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten later
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(index.router)

    @app.on_event("startup")
    def on_startup():
        init_db()

    @app.get("/")
    def root():
        return {"status": "ok", "app": settings.app_name, "env": settings.env}

    return app

app = create_app()