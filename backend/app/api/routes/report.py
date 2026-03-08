from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ...database import get_session
from ...services.report_generator import build_audit_report_pdf


router = APIRouter()


@router.get(
  "/audit-report",
  summary="Download audit report as PDF (legacy)",
  description="Legacy endpoint; prefer GET /export-audit-report. Returns the governance audit report as PDF.",
  response_class=Response,
)
async def get_audit_report_pdf(
  db: Session = Depends(get_session),
) -> Response:
  buffer = build_audit_report_pdf(db)
  filename = f"audit-report-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.pdf"
  return Response(
    content=buffer.read(),
    media_type="application/pdf",
    headers={
      "Content-Disposition": f'attachment; filename=\"{filename}\"',
    },
  )


@router.get(
  "/export-audit-report",
  summary="Download governance audit report as PDF",
  description=(
    "Governance audit report including task description, AI decision output, risk classification, "
    "confidence score, reasoning steps, human approval status, blockchain transaction hash, "
    "timestamps, and governance score summary."
  ),
  response_class=Response,
)
async def export_audit_report_pdf(
  db: Session = Depends(get_session),
) -> Response:
  """
  Generate and download the governance audit report as a PDF.
  """
  buffer = build_audit_report_pdf(db)
  filename = f"export-audit-report-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.pdf"
  return Response(
    content=buffer.read(),
    media_type="application/pdf",
    headers={
      "Content-Disposition": f'attachment; filename=\"{filename}\"',
    },
  )
