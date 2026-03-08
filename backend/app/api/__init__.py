from fastapi import APIRouter

from .routes import audit, decision, risk, task, governance, timeline, monitoring, report, analytics, demo, dashboard

router = APIRouter()

router.include_router(task.router, tags=["task"])
router.include_router(demo.router, tags=["demo"])
router.include_router(decision.router, tags=["decision"])
router.include_router(risk.router, tags=["risk"])
router.include_router(audit.router, tags=["audit"])
router.include_router(governance.router, tags=["governance"])
router.include_router(timeline.router, tags=["timeline"])
router.include_router(monitoring.router, tags=["monitoring"])
router.include_router(report.router, tags=["report"])
router.include_router(analytics.router, tags=["analytics"])
router.include_router(dashboard.router, tags=["dashboard"])

