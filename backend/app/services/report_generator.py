from __future__ import annotations

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
  Paragraph,
  Spacer,
  Table,
  TableStyle,
  SimpleDocTemplate,
  ListFlowable,
  ListItem,
  HRFlowable,
)
from sqlalchemy.orm import Session

from ..database import AuditLogORM, DecisionTraceORM, Task
from ..services.governance_score import compute_governance_score
from ..utils import fmt_ts


DARK_BG = colors.HexColor("#111827")
ACCENT = colors.HexColor("#F5C542")
LIGHT_TEXT = colors.HexColor("#E5E7EB")
MUTED_TEXT = colors.HexColor("#9CA3AF")
BORDER_COLOR = colors.HexColor("#374151")


def _p(text: str, style) -> Paragraph:
  safe = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
  return Paragraph(safe, style)


def build_audit_report_pdf(db: Session) -> BytesIO:
  buffer = BytesIO()
  doc = SimpleDocTemplate(
    buffer,
    pagesize=A4,
    rightMargin=0.7 * inch,
    leftMargin=0.7 * inch,
    topMargin=0.7 * inch,
    bottomMargin=0.7 * inch,
  )
  styles = getSampleStyleSheet()

  title_style = ParagraphStyle(
    name="ReportTitle", parent=styles["Heading1"],
    fontSize=20, spaceAfter=4, textColor=LIGHT_TEXT,
  )
  subtitle_style = ParagraphStyle(
    name="Subtitle", parent=styles["Normal"],
    fontSize=10, textColor=MUTED_TEXT, spaceAfter=16,
  )
  heading_style = ParagraphStyle(
    name="SectionHeading", parent=styles["Heading2"],
    fontSize=13, spaceAfter=8, spaceBefore=16, textColor=LIGHT_TEXT,
  )
  body_style = ParagraphStyle(
    name="Body", parent=styles["Normal"],
    fontSize=9, textColor=LIGHT_TEXT, leading=13,
  )
  cell_style = ParagraphStyle(
    name="CellText", parent=body_style,
    fontSize=8, leading=10, wordWrap="CJK",
  )
  cell_bold = ParagraphStyle(
    name="CellBold", parent=cell_style,
    fontName="Helvetica-Bold", textColor=ACCENT,
  )
  cell_header = ParagraphStyle(
    name="CellHeader", parent=cell_style,
    fontName="Helvetica-Bold", textColor=colors.white,
  )

  story = []
  aw = A4[0] - doc.leftMargin - doc.rightMargin

  # --- Title ---
  story.append(Paragraph("AuditSentinel Governance Report", title_style))
  story.append(Paragraph(f"Generated {fmt_ts(datetime.utcnow())} UTC", subtitle_style))
  story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceAfter=12))

  # --- Task Summary ---
  latest_decision = (
    db.query(DecisionTraceORM).order_by(DecisionTraceORM.created_at.desc()).first()
  )

  story.append(Paragraph("1. Task Summary", heading_style))
  if latest_decision:
    task_row = None
    if latest_decision.task_id:
      task_row = db.query(Task).filter(Task.id == latest_decision.task_id).first()

    task_description = (task_row.description if task_row else "") or "\u2014"
    risk_label = latest_decision.risk.value if latest_decision.risk else "\u2014"
    confidence_pct = f"{round((latest_decision.confidence or 0.0) * 100)}%"

    audit_entry = None
    if latest_decision.task_id:
      audit_entry = (
        db.query(AuditLogORM)
        .filter(AuditLogORM.task_id == latest_decision.task_id)
        .order_by(AuditLogORM.created_at.desc()).first()
      )
    if audit_entry is None:
      audit_entry = db.query(AuditLogORM).order_by(AuditLogORM.created_at.desc()).first()

    human_status = audit_entry.status if audit_entry else "\u2014"
    tx_hash = audit_entry.tx_hash if audit_entry else None
    decision_ts = fmt_ts(latest_decision.created_at)
    tx_ts = fmt_ts(audit_entry.timestamp or audit_entry.created_at) if audit_entry else "\u2014"

    rows = [
      [_p("Task Description", cell_bold), _p(task_description[:500], cell_style)],
      [_p("AI Decision Output", cell_bold), _p((latest_decision.output or "")[:500], cell_style)],
      [_p("Risk Classification", cell_bold), _p(risk_label.upper(), cell_style)],
      [_p("Confidence Score", cell_bold), _p(confidence_pct, cell_style)],
      [_p("Human Approval Status", cell_bold), _p(human_status.capitalize(), cell_style)],
      [_p("Blockchain Tx Hash", cell_bold), _p(tx_hash or "\u2014", cell_style)],
      [_p("Timestamp", cell_bold), _p(decision_ts, cell_style)],
    ]
    t = Table(rows, colWidths=[130, aw - 130])
    t.setStyle(TableStyle([
      ("VALIGN", (0, 0), (-1, -1), "TOP"),
      ("GRID", (0, 0), (-1, -1), 0.4, BORDER_COLOR),
      ("BACKGROUND", (0, 0), (0, -1), DARK_BG),
      ("LEFTPADDING", (0, 0), (-1, -1), 6),
      ("RIGHTPADDING", (0, 0), (-1, -1), 6),
      ("TOPPADDING", (0, 0), (-1, -1), 5),
      ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)

    # --- AI Reasoning ---
    story.append(Spacer(1, 12))
    story.append(Paragraph("2. AI Reasoning Steps", heading_style))
    reasoning_text = latest_decision.reasoning or ""
    steps = [s for s in reasoning_text.splitlines() if s.strip()][:8]
    if steps:
      bullet_items = [
        ListItem(Paragraph(step, body_style), bulletFontName="Helvetica", bulletFontSize=8)
        for step in steps
      ]
      story.append(ListFlowable(
        bullet_items, bulletType="bullet", start="circle",
        bulletFontName="Helvetica", bulletFontSize=8, leftIndent=12,
      ))
    else:
      story.append(Paragraph("No reasoning steps recorded.", body_style))

    # --- Blockchain Verification ---
    story.append(Spacer(1, 12))
    story.append(Paragraph("3. Blockchain Verification", heading_style))
    if tx_hash:
      story.append(Paragraph(
        f"Transaction recorded on-chain at {tx_ts}. "
        f"Hash: {tx_hash}", body_style
      ))
    else:
      story.append(Paragraph("No blockchain transaction recorded for this task.", body_style))
  else:
    story.append(Paragraph("No AI decision recorded yet.", body_style))

  # --- Recent Audit Logs ---
  story.append(Spacer(1, 16))
  story.append(Paragraph("4. Recent Audit Logs", heading_style))
  audit_rows = (
    db.query(AuditLogORM).order_by(AuditLogORM.created_at.desc()).limit(10).all()
  )
  if audit_rows:
    header = [
      _p("Action", cell_header), _p("Risk", cell_header),
      _p("Status", cell_header), _p("Tx Hash", cell_header),
      _p("Timestamp", cell_header),
    ]
    data = [header]
    for row in audit_rows:
      data.append([
        _p((row.action_description or "")[:70], cell_style),
        _p((row.risk.value if row.risk else "\u2014").upper(), cell_style),
        _p((row.status or "\u2014").capitalize(), cell_style),
        _p((row.tx_hash[:18] + "..." if row.tx_hash else "\u2014"), cell_style),
        _p(fmt_ts(row.timestamp or row.created_at), cell_style),
      ])
    cw = [aw * 0.28, aw * 0.10, aw * 0.12, aw * 0.28, aw * 0.22]
    lt = Table(data, colWidths=cw)
    lt.setStyle(TableStyle([
      ("VALIGN", (0, 0), (-1, -1), "TOP"),
      ("BACKGROUND", (0, 0), (-1, 0), DARK_BG),
      ("GRID", (0, 0), (-1, -1), 0.4, BORDER_COLOR),
      ("LEFTPADDING", (0, 0), (-1, -1), 4),
      ("RIGHTPADDING", (0, 0), (-1, -1), 4),
      ("TOPPADDING", (0, 0), (-1, -1), 4),
      ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(lt)
  else:
    story.append(Paragraph("No audit log entries yet.", body_style))

  # --- Governance Score ---
  story.append(Spacer(1, 16))
  story.append(Paragraph("5. Governance Score Summary", heading_style))
  score = compute_governance_score(db)
  score_data = [
    [_p("Metric", cell_header), _p("Value", cell_header)],
    [_p("Overall Score", cell_bold), _p(f"{score.score} / 100", cell_style)],
    [_p("Total Tasks", cell_bold), _p(str(score.total_tasks), cell_style)],
    [_p("High-Risk Actions", cell_bold), _p(str(score.high_risk_actions), cell_style)],
    [_p("Rejected Decisions", cell_bold), _p(str(score.rejected_decisions), cell_style)],
    [_p("Blockchain-Verified Logs", cell_bold), _p(str(score.blockchain_verified_logs), cell_style)],
  ]
  st = Table(score_data, colWidths=[aw * 0.5, aw * 0.5])
  st.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BACKGROUND", (0, 0), (-1, 0), DARK_BG),
    ("GRID", (0, 0), (-1, -1), 0.4, BORDER_COLOR),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
  ]))
  story.append(st)

  doc.build(story)
  buffer.seek(0)
  return buffer
