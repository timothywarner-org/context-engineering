"""Configuration management for WARNERCO Robotics Schematica."""

from enum import Enum
from pathlib import Path
from typing import Optional

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
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # LLM Provider
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
    def has_llm_config(self) -> bool:
        """Check if LLM configuration is available."""
        return bool(self.openai_api_key or (self.azure_openai_endpoint and self.azure_openai_api_key))


# Global settings instance
settings = Settings()
