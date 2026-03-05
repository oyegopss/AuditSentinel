from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .domain.models import AuditLogEntry, RiskLevel


@dataclass
class BlockchainReceipt:
  action_hash: str
  tx_hash: str
  timestamp: datetime


def compute_action_hash(
  action_description: str,
  timestamp: datetime,
  user: str
) -> str:
  """
  Generate a deterministic SHA256 hash from:
  - action description
  - timestamp (ISO string)
  - user identifier

  This hash is what we send to the on‑chain AuditSentinel contract.
  """
  payload = (
    f"{action_description}|{timestamp.isoformat()}|{user}"
  ).encode("utf-8")
  return hashlib.sha256(payload).hexdigest()


async def log_high_risk_action_to_chain(
  action_description: str,
  user: str
) -> BlockchainReceipt:
  """
  Stubbed blockchain logger.

  In production, this function should:
  - connect to a Polygon testnet RPC endpoint
  - sign and send a transaction to the AuditSentinel Solidity contract
  - wait for confirmation and return the real transaction hash + block timestamp
  """
  now = datetime.now(timezone.utc)
  action_hash = compute_action_hash(action_description, now, user)

  # Demo‑only transaction hash placeholder
  tx_hash = "0x" + hashlib.sha1(action_hash.encode("utf-8")).hexdigest()

  return BlockchainReceipt(
    action_hash=action_hash,
    tx_hash=tx_hash,
    timestamp=now
  )


def build_audit_log_entry(
  description: str,
  risk: RiskLevel,
  receipt: Optional[BlockchainReceipt] = None,
  status: str = "approved"
) -> AuditLogEntry:
  if receipt:
    action_hash = receipt.action_hash
    ts = receipt.timestamp
  else:
    ts = datetime.now(timezone.utc)
    # System‑generated hash when there is no external user context
    action_hash = compute_action_hash(description, ts, user="system")

  return AuditLogEntry(
    action_hash=action_hash,
    tx_hash=receipt.tx_hash if receipt else None,
    timestamp=ts,
    action_description=description,
    risk=risk,
    status=status
  )


