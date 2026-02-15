"""
Core application configuration.
Loads and validates environment variables.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "AI Boilerplate API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: list[str] = Field(default=["http://localhost:3000"])

    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DB_POOL_SIZE: int = Field(default=20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=40, env="DB_MAX_OVERFLOW")

    # Supabase
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY")
    SUPABASE_JWT_SECRET: str = Field(..., env="SUPABASE_JWT_SECRET")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_MAX_CONNECTIONS: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")

    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")

    # Weaviate Vector Database
    WEAVIATE_URL: str = Field(default="http://localhost:8080", env="WEAVIATE_URL")
    WEAVIATE_API_KEY: Optional[str] = Field(default=None, env="WEAVIATE_API_KEY")
    WEAVIATE_CLASS_NAME: str = Field(default="EmbeddingRecord", env="WEAVIATE_CLASS_NAME")
    WEAVIATE_TIMEOUT_SECONDS: int = Field(default=30, env="WEAVIATE_TIMEOUT_SECONDS")

    # AI Providers
    CEREBRAS_API_KEY: str = Field(..., env="CEREBRAS_API_KEY")
    CEREBRAS_MODEL: str = Field(default="llama3.1-8b", env="CEREBRAS_MODEL")
    CEREBRAS_MAX_TOKENS: int = Field(default=1024, env="CEREBRAS_MAX_TOKENS")
    CEREBRAS_TEMPERATURE: float = Field(default=0.7, env="CEREBRAS_TEMPERATURE")

    VOYAGE_API_KEY: str = Field(..., env="VOYAGE_API_KEY")
    VOYAGE_MODEL: str = Field(default="voyage-2", env="VOYAGE_MODEL")
    VOYAGE_EMBEDDING_DIMENSION: int = Field(default=1024, env="VOYAGE_EMBEDDING_DIMENSION")

    # n8n Integration
    N8N_WEBHOOK_URL: Optional[str] = Field(default=None, env="N8N_WEBHOOK_URL")
    N8N_API_KEY: Optional[str] = Field(default=None, env="N8N_API_KEY")

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "json"  # json or text

    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
