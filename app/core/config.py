"""Centralized configuration for the application.

Loads environment variables for Groq LLM integration and PostgreSQL database storage.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and configuration."""

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "qwen/qwen3.8-27b"
    GROQ_TEMPERATURE: float = 0.1
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/answer_book"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

