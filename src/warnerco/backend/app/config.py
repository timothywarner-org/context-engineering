"""Configuration management for WARNERCO Robotics Schematica."""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MemoryBackend(str, Enum):
    """Available memory backend implementations."""

    JSON = "json"
    CHROMA = "chroma"
    AZURE_SEARCH = "azure_search"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Memory Backend Selection
    memory_backend: MemoryBackend = MemoryBackend.CHROMA

    # Server Configuration
    # Bind to loopback so the address uvicorn logs (http://127.0.0.1:8000) is the
    # one you actually browse. 0.0.0.0 binds all interfaces but logs an
    # unbrowsable URL on Windows; override host in .env if you need LAN access.
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = Field(default=False, validation_alias="APP_DEBUG")

    # Azure APIM (optional front-end)
    apim_subscription_key: Optional[str] = None

    # LLM Provider
    # Anthropic is preferred for the reason node (single verified key for the
    # whole course); OpenAI/Azure remain as fallbacks.
    anthropic_api_key: Optional[str] = None
    claude_model: str = "claude-sonnet-4-6"
    openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_deployment: str = "gpt-4o-mini"  # Chat model for reasoning
    azure_openai_embedding_deployment: str = "text-embedding-ada-002"  # Embeddings
    azure_openai_api_version: str = "2024-08-01-preview"

    # Azure AI Search
    azure_search_endpoint: Optional[str] = None
    azure_search_key: Optional[str] = None
    azure_search_index: str = "warnerco-schematics"

    # Chroma Configuration
    chroma_persist_dir: str = "../data/chroma"

    # JSON Store Configuration
    json_schematics_path: str = "../data/schematics/schematics.json"

    # Telemetry
    telemetry_enabled: bool = True

    # Scratchpad Memory Configuration (persistent SQLite storage)
    scratchpad_db_path: str = "data/scratchpad/notes.db"  # SQLite database path (relative to backend/)
    scratchpad_inject_budget: int = 1500  # Tokens for LangGraph injection

    # =========================================================================
    # Episodic Memory (CoALA Tier 2)
    # =========================================================================
    # Episodic memory records timestamped session events (turns, tool calls,
    # observations) and retrieves them via Park et al.'s scoring formula:
    #   total = α_recency·recency + α_importance·importance + α_relevance·relevance
    # See app/adapters/episodic_store.py for the implementation.
    episodic_db_path: str = "data/episodic/events.db"
    episodic_max_retrieval_k: int = 5
    episodic_recency_half_life_hours: float = 24.0
    episodic_weight_recency: float = 0.4
    episodic_weight_importance: float = 0.3
    episodic_weight_relevance: float = 0.3

    @property
    def chroma_path(self) -> Path:
        """Get absolute path to Chroma persist directory."""
        # Path relative to backend root: backend/data/chroma
        # __file__ = backend/app/config.py, so .parent.parent = backend/
        return Path(__file__).parent.parent.resolve() / "data" / "chroma"

    @property
    def json_path(self) -> Path:
        """Get absolute path to JSON schematics file."""
        # Path relative to backend root: backend/data/schematics/schematics.json
        # __file__ = backend/app/config.py, so .parent.parent = backend/
        return Path(__file__).parent.parent.resolve() / "data" / "schematics" / "schematics.json"

    @property
    def scratchpad_path(self) -> Path:
        """Get absolute path to scratchpad SQLite database."""
        return Path(__file__).parent.parent.resolve() / self.scratchpad_db_path

    @property
    def episodic_path(self) -> Path:
        """Get absolute path to episodic SQLite database."""
        return Path(__file__).parent.parent.resolve() / self.episodic_db_path

    @property
    def has_llm_config(self) -> bool:
        """Check if LLM configuration is available (any provider)."""
        return bool(
            self.anthropic_api_key
            or self.openai_api_key
            or (self.azure_openai_endpoint and self.azure_openai_api_key)
        )


# Global settings instance
settings = Settings()
