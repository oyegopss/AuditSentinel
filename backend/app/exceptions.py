"""
Custom exceptions for global error handling.
AI agent, database, and blockchain failures map to consistent JSON responses.
"""


class AuditSentinelError(Exception):
  """Base for AuditSentinel API errors."""

  def __init__(self, message: str, status_code: int = 500):
    self.message = message
    self.status_code = status_code
    super().__init__(message)


class AgentError(AuditSentinelError):
  """Raised when the AI agent (planning/execution) fails."""

  def __init__(self, message: str, status_code: int = 502):
    super().__init__(message, status_code=status_code)


class DatabaseError(AuditSentinelError):
  """Raised when a database operation fails."""

  def __init__(self, message: str, status_code: int = 503):
    super().__init__(message, status_code=status_code)


class BlockchainError(AuditSentinelError):
  """Raised when blockchain logging or verification fails."""

  def __init__(self, message: str, status_code: int = 503):
    super().__init__(message, status_code=status_code)


class APIError(AuditSentinelError):
  """General API / business logic failures."""

  def __init__(self, message: str, status_code: int = 400):
    super().__init__(message, status_code=status_code)
