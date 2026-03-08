from __future__ import annotations

import hashlib
from datetime import datetime


def sha256_action_hash(
  action: str,
  timestamp: datetime,
  user_id: str,
) -> str:
  """
  Generate SHA256 hash of (action, timestamp, user_id) for secure blockchain logging.

  Payload: action|timestamp_iso|user_id. Same inputs produce the same hash.
  The hash is stored in the smart contract; only the hash is sent on-chain.
  """
  payload = f"{action}|{timestamp.isoformat()}|{user_id}".encode("utf-8")
  return hashlib.sha256(payload).hexdigest()
