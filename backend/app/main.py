from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router
from .db.session import Base, engine


def create_app() -> FastAPI:
  app = FastAPI(
    title="AuditSentinel API",
    version="0.1.0",
    description=(
      "Risk‑aware AI governance backend for the AuditSentinel demo. "
      "Provides task submission, explainability, risk simulation, "
      "human approval, and blockchain audit logging endpoints."
    )
  )

  app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
  )

  @app.on_event("startup")
  def on_startup() -> None:
    # Ensure tables exist for demo purposes. In production, prefer migrations.
    Base.metadata.create_all(bind=engine)

  app.include_router(api_router)
  return app


app = create_app()


