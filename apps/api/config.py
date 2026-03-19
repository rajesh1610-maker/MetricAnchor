"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM
    llm_provider: Literal["openai", "anthropic", "openai_compatible"] = "openai"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o"
    llm_base_url: str = ""
    llm_max_tokens: int = 2048
    llm_send_sample_rows: bool = True

    # Storage
    data_dir: str = "./data"
    max_upload_bytes: int = 524_288_000  # 500 MB

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/metricanchor.db"

    # API
    cors_origins: list[str] = Field(default=["http://localhost:3000"])
    api_debug: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
