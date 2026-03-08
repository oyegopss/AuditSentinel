from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from web3 import Web3

from ..config import get_settings
from ..domain.models import AuditLogEntry
from ..risk_engine import RiskLevel
from ..utils.hashing import sha256_action_hash
from ..logging_config import get_logger


logger = get_logger("blockchain")

# Polygon Amoy testnet
AMOY_RPC = "https://rpc-amoy.polygon.technology"
AMOY_CHAIN_ID = 80002


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
  """Delegate to shared SHA256 action-hash utility before sending to blockchain."""
  return sha256_action_hash(action_description, timestamp, user)


def _send_real_tx_to_amoy(
  action_description: str,
  risk_level: str,
  action_hash: str,
  rpc_url: str,
  private_key: str,
  chain_id: int = AMOY_CHAIN_ID,
) -> str:
  """
  Send a real transaction to Polygon Amoy testnet. Uses 0 value, self-transfer,
  with action and risk encoded in data. Returns the transaction hash (0x-prefixed hex).
  """
  w3 = Web3(Web3.HTTPProvider(rpc_url))
  if not w3.is_connected():
    raise ConnectionError(f"Cannot connect to RPC: {rpc_url}")

  account = w3.eth.account.from_key(private_key)
  # Encode audit payload in tx data (action|risk); explorer will show input data
  data_utf8 = f"{action_description[:200]}|{risk_level}"
  data_hex = "0x" + data_utf8.encode("utf-8").hex()

  tx = {
    "from": account.address,
    "to": account.address,
    "value": 0,
    "gas": 200000,
    "chainId": chain_id,
    "nonce": w3.eth.get_transaction_count(account.address),
    "data": data_hex,
  }
  # Use dynamic gas price from chain
  tx["gasPrice"] = w3.eth.gas_price

  signed = w3.eth.account.sign_transaction(tx, private_key)
  tx_hash_bytes = w3.eth.send_raw_transaction(signed.raw_transaction)
  return w3.to_hex(tx_hash_bytes)


def _generate_mock_tx_fallback() -> str:
  """
  Fallback mock tx hash when no private key is configured.
  Only used when POLYGON_PRIVATE_KEY (or blockchain_private_key) is not set.
  """
  import uuid
  base = uuid.uuid4().hex
  body = (base * 2)[:64]
  return "0x" + body


async def log_high_risk_action_to_chain(
  action_description: str,
  user: str,
  risk_level: Optional[RiskLevel] = None,
) -> BlockchainReceipt:
  """
  For HIGH/CRITICAL approved actions: compute action hash and send a real
  transaction to Polygon Amoy testnet when POLYGON_PRIVATE_KEY (or
  blockchain_private_key) is set. Otherwise fall back to a mock tx hash
  and log a warning. Returns BlockchainReceipt with action_hash, tx_hash, timestamp.
  """
  now = datetime.now(timezone.utc)
  action_hash = sha256_action_hash(action_description, now, user)
  risk_str = (risk_level.value if risk_level else "high")

  settings = get_settings()
  rpc_url = settings.blockchain_rpc_url or AMOY_RPC
  private_key = os.getenv("POLYGON_PRIVATE_KEY") or settings.blockchain_private_key
  chain_id = settings.blockchain_chain_id or AMOY_CHAIN_ID

  tx_hash: str
  if private_key:
    try:
      tx_hash = await asyncio.to_thread(
        _send_real_tx_to_amoy,
        action_description,
        risk_str,
        action_hash,
        rpc_url,
        private_key,
        chain_id,
      )
      logger.info(
        "Blockchain transaction sent to Polygon Amoy",
        extra={
          "event": "blockchain_transaction",
          "action_hash": action_hash,
          "tx_hash": tx_hash,
          "user": user,
          "timestamp": now.isoformat(),
        },
      )
    except Exception as e:
      logger.exception("Real blockchain tx failed: %s", e)
      raise
  else:
    tx_hash = _generate_mock_tx_fallback()
    logger.warning(
      "POLYGON_PRIVATE_KEY (or blockchain_private_key) not set; using mock tx hash. Set env for real on-chain logging.",
      extra={"event": "blockchain_mock_fallback", "tx_hash": tx_hash},
    )

  return BlockchainReceipt(
    action_hash=action_hash,
    tx_hash=tx_hash,
    timestamp=now,
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
    action_hash = sha256_action_hash(description, ts, user_id="system")

  return AuditLogEntry(
    action_hash=action_hash,
    tx_hash=receipt.tx_hash if receipt else None,
    timestamp=ts,
    action_description=description,
    risk=risk,
    status=status
  )
