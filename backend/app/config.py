"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application ----
    app_name: str = "ChainSentinel"
    app_version: str = "0.1.0"
    debug: bool = False
    secret_key: str = "change-me-in-production"
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]

    # ---- Database ----
    database_url: str = (
        "postgresql+asyncpg://chainsentinel:chainsentinel@localhost:5432/chainsentinel"
    )

    # ---- Redis ----
    redis_url: str = "redis://localhost:6379/0"

    # ---- Neo4j ----
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "chainsentinel"

    # ---- Celery ----
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ---- JWT ----
    jwt_secret_key: str = "jwt-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ---- Blockchain Provider ----
    provider_mode: Literal["demo", "live"] = "demo"
    etherscan_api_key: str = ""
    alchemy_api_key: str = ""

    # ---- LLM ----
    llm_provider: Literal["openai", "ollama"] = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # ---- Rate Limiting ----
    rate_limit_per_minute: int = 60

    # ---- Logging ----
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
