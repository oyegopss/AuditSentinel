from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from .api import router as api_router
from .cache import clear_decision_cache
from .database import Base, engine
from .exceptions import AgentError, AuditSentinelError, BlockchainError, DatabaseError
from .logging_config import setup_logging


def _error_json(detail: str, error_type: str, status_code: int) -> dict:
  return {"detail": detail, "error_type": error_type, "status_code": status_code}


def create_app() -> FastAPI:
  setup_logging()

  app = FastAPI(
    title="AuditSentinel API",
    version="0.1.0",
    description=(
      "Risk-aware AI governance backend. Key areas:\n\n"
      "- **Task submission** — Submit natural-language tasks; agent returns decision, risk, and approval flag.\n"
      "- **Risk simulation** — Simulate risk for scenarios (e.g. loan, DB delete, healthcare, trading) before approval.\n"
      "- **Approval workflow** — Human-in-the-loop approve/reject; approved high-risk actions trigger blockchain logging.\n"
      "- **Blockchain logging** — SHA256 action hashes stored on-chain; audit log includes transaction hash and timestamp.\n"
      "- **Governance score** — 0–100 score from high-risk actions, rejections, and on-chain verification."
    ),
  )

  # ---------------------------------------------------------------------------
  # Global exception handlers
  # ---------------------------------------------------------------------------

  @app.exception_handler(RequestValidationError)
  async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
  ) -> JSONResponse:
    """Pydantic validation errors (invalid body/query/path)."""
    return JSONResponse(
      status_code=422,
      content={"detail": exc.errors(), "error_type": "validation_error", "status_code": 422},
    )

  @app.exception_handler(AgentError)
  async def agent_exception_handler(
    request: Request,
    exc: AgentError,
  ) -> JSONResponse:
    """AI agent (planning/execution) failures."""
    return JSONResponse(
      status_code=exc.status_code,
      content=_error_json(exc.message, "agent_error", exc.status_code),
    )

  @app.exception_handler(DatabaseError)
  async def database_error_handler(
    request: Request,
    exc: DatabaseError,
  ) -> JSONResponse:
    """Explicit database errors."""
    return JSONResponse(
      status_code=exc.status_code,
      content=_error_json(exc.message, "database_error", exc.status_code),
    )

  @app.exception_handler(SQLAlchemyError)
  async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
  ) -> JSONResponse:
    """Uncaught database/ORM errors."""
    return JSONResponse(
      status_code=503,
      content=_error_json("Database operation failed.", "database_error", 503),
    )

  @app.exception_handler(BlockchainError)
  async def blockchain_exception_handler(
    request: Request,
    exc: BlockchainError,
  ) -> JSONResponse:
    """Blockchain logging/verification failures."""
    return JSONResponse(
      status_code=exc.status_code,
      content=_error_json(exc.message, "blockchain_error", exc.status_code),
    )

  @app.exception_handler(AuditSentinelError)
  async def audit_sentinel_exception_handler(
    request: Request,
    exc: AuditSentinelError,
  ) -> JSONResponse:
    """Other custom API/business errors."""
    return JSONResponse(
      status_code=exc.status_code,
      content=_error_json(exc.message, "api_error", exc.status_code),
    )

  @app.exception_handler(Exception)
  async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
  ) -> JSONResponse:
    """Catch-all; avoid leaking internals."""
    return JSONResponse(
      status_code=500,
      content=_error_json("An unexpected error occurred.", "internal_error", 500),
    )

  # ---------------------------------------------------------------------------
  # Middleware
  # ---------------------------------------------------------------------------

  app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
  )

  @app.get("/")
  def root(request: Request):
    """Redirect browser to frontend; API clients can use Accept header or /docs."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
      return RedirectResponse(url="http://localhost:3000/dashboard", status_code=302)
    return {
      "message": "AuditSentinel API",
      "frontend": "Open http://localhost:3000 for the AuditSentinel dashboard.",
      "docs": "/docs",
      "openapi": "/openapi.json",
    }

  FRONTEND_URL = "http://localhost:3000"

  @app.get("/AuditSentinel")
  @app.get("/AuditSentinel/")
  @app.get("/dashboard")
  @app.get("/dashboard/")
  @app.get("/decision")
  @app.get("/approve")
  @app.get("/audit-logs")
  @app.get("/governance")
  @app.get("/monitoring")
  @app.get("/analytics")
  def frontend_redirect(request: Request):
    """Redirect browser requests for UI routes to the frontend so the app opens correctly."""
    path = request.url.path.rstrip("/") or "/dashboard"
    if path == "/AuditSentinel":
      path = "/dashboard"
    return RedirectResponse(url=f"{FRONTEND_URL}{path}", status_code=302)

  @app.on_event("startup")
  def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    clear_decision_cache()

  app.include_router(api_router)
  return app


app = create_app()
