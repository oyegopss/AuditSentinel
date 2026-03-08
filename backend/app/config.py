"""
Configuration module using Pydantic settings.
Loads environment variables for database, AI API, and blockchain credentials.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Database
    # -------------------------------------------------------------------------
    database_url: str = Field(
        default="sqlite:///./auditsentinel.db",
        description="Database URL (SQLite for local dev, or PostgreSQL e.g. postgresql+psycopg2://user:pass@host:5432/db).",
    )

    # -------------------------------------------------------------------------
    # AI API
    # -------------------------------------------------------------------------
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for LangChain/LLM calls.",
    )
    ai_api_base_url: Optional[str] = Field(
        default=None,
        description="Optional base URL for AI API (e.g. OpenAI-compatible endpoint).",
    )
    ai_model: Optional[str] = Field(
        default=None,
        description="Default AI model name (e.g. gpt-4).",
    )

    # -------------------------------------------------------------------------
    # Blockchain
    # -------------------------------------------------------------------------
    blockchain_rpc_url: Optional[str] = Field(
        default=None,
        description="Polygon RPC URL (e.g. https://rpc-amoy.polygon.technology).",
    )
    blockchain_contract_address: Optional[str] = Field(
        default=None,
        description="Deployed AuditSentinel audit contract address.",
    )
    blockchain_private_key: Optional[str] = Field(
        default=None,
        description="Private key for signing transactions (keep secret, use env only). Also supports POLYGON_PRIVATE_KEY in logger.",
    )
    blockchain_chain_id: Optional[int] = Field(
        default=80002,
        description="Chain ID (80002 for Polygon Amoy testnet).",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance (loads env once)."""
    return Settings()
