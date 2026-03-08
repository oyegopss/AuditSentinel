"""
Blockchain event listener for the audit log smart contract.
Listens for AIActionLogged events and stores transaction hash and timestamp in the database.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from web3 import Web3
from web3.exceptions import BlockNotFound
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import SessionLocal, AuditLog
from ..risk_engine import RiskLevel
from ..logging_config import get_logger


logger = get_logger("blockchain.listener")

# Minimal ABI for AIActionLogged(address,uint256,address) - Solidity bytes32 indexed is topic, uint256 indexed
# Event signature: AIActionLogged(bytes32 indexed actionHash, uint256 indexed timestamp, address indexed logger)
AUDIT_EVENT_ABI = [
  {
    "type": "event",
    "name": "AIActionLogged",
    "inputs": [
      {"name": "actionHash", "type": "bytes32", "indexed": True},
      {"name": "timestamp", "type": "uint256", "indexed": True},
      {"name": "logger", "type": "address", "indexed": True},
    ],
  }
]


def _action_hash_hex(bytes32_value) -> str:
  """Normalize bytes32 to 64-char hex (no 0x) to match DB."""
  if hasattr(bytes32_value, "hex"):
    return bytes32_value.hex()
  s = str(bytes32_value).lower()
  if s.startswith("0x"):
    s = s[2:]
  return s[:64]


def _process_event(
  action_hash_hex: str,
  tx_hash: str,
  on_chain_timestamp: int,
  db: Session,
) -> None:
  """Store or update audit log with transaction hash and timestamp."""
  ts = datetime.fromtimestamp(on_chain_timestamp, tz=timezone.utc)
  row = db.query(AuditLog).filter(AuditLog.action_hash == action_hash_hex).first()
  if row:
    row.tx_hash = tx_hash
    row.timestamp = ts
    db.commit()
    logger.info(
      "Updated audit log from chain event",
      extra={
        "event": "blockchain_listener",
        "action_hash": action_hash_hex[:16] + "..",
        "tx_hash": tx_hash[:18] + "..",
        "timestamp": ts.isoformat(),
      },
    )
  else:
    entry = AuditLog(
      action_hash=action_hash_hex,
      tx_hash=tx_hash,
      timestamp=ts,
      action_description="On-chain log (listener)",
      risk=RiskLevel.LOW,
      status="logged",
    )
    db.add(entry)
    db.commit()
    logger.info(
      "Inserted audit log from chain event",
      extra={
        "event": "blockchain_listener",
        "action_hash": action_hash_hex[:16] + "..",
        "tx_hash": tx_hash[:18] + "..",
      },
    )


def process_log_entry(
  contract_address: str,
  w3: Web3,
  log_entry: dict,
  db: Session,
) -> None:
  """
  Process a single AIActionLogged log entry: decode and store tx_hash + timestamp.
  """
  try:
    contract = w3.eth.contract(
      address=Web3.to_checksum_address(contract_address),
      abi=AUDIT_EVENT_ABI,
    )
    event = contract.events.AIActionLogged().process_log(log_entry)
  except Exception as e:
    logger.warning("Failed to decode event", extra={"error": str(e)[:100]})
    return
  action_hash_raw = event.args.actionHash
  action_hash_hex = _action_hash_hex(action_hash_raw)
  tx_hash = log_entry.get("transactionHash") if isinstance(log_entry, dict) else getattr(log_entry, "transactionHash", None)
  if tx_hash is None:
    return
  if hasattr(tx_hash, "hex"):
    tx_hash = "0x" + tx_hash.hex()
  elif not isinstance(tx_hash, str) or not tx_hash.startswith("0x"):
    tx_hash = "0x" + str(tx_hash)
  on_chain_ts = event.args.timestamp
  if hasattr(on_chain_ts, "__int__"):
    on_chain_ts = int(on_chain_ts)
  _process_event(action_hash_hex, tx_hash, on_chain_ts, db)


def fetch_and_process_events(
  from_block: int = 0,
  to_block: Optional[int] = None,
) -> int:
  """
  Fetch AIActionLogged logs in block range and store tx_hash + timestamp in DB.
  Returns number of events processed.
  """
  settings = get_settings()
  rpc_url = settings.blockchain_rpc_url
  contract_address = settings.blockchain_contract_address
  if not rpc_url or not contract_address:
    logger.debug("Blockchain RPC or contract address not set; listener skipped")
    return 0
  try:
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
      return 0
  except Exception as e:
    logger.warning("Web3 connection failed", extra={"error": str(e)[:100]})
    return 0

  if to_block is None:
    try:
      to_block = w3.eth.block_number
    except Exception:
      return 0
  contract = w3.eth.contract(
    address=Web3.to_checksum_address(contract_address),
    abi=AUDIT_EVENT_ABI,
  )
  try:
    logs = contract.events.AIActionLogged().get_logs(from_block=from_block, to_block=to_block)
  except (BlockNotFound, ValueError) as e:
    logger.warning("get_logs failed", extra={"error": str(e)[:100]})
    return 0
  db = SessionLocal()
  count = 0
  try:
    for log in logs:
      try:
        process_log_entry(contract_address, w3, dict(log), db)
        count += 1
      except Exception as e:
        logger.warning("Process log failed", extra={"error": str(e)[:100]})
  finally:
    db.close()
  return count
