from fastapi import APIRouter

from .routes import audit, decision, risk, task

router = APIRouter()

router.include_router(task.router, tags=["task"])
router.include_router(decision.router, tags=["decision"])
router.include_router(risk.router, tags=["risk"])
router.include_router(audit.router, tags=["audit"])

