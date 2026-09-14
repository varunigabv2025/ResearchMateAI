"""
Application configuration using pydantic-settings.
Loads environment variables from .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "ResearchMate AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./test.db"  # Default for testing
    
    # LLM Configuration (OpenRouter)
    LLM_API_KEY: str = "test-key"  # Default for testing
    LLM_MODEL: str = "openrouter/free"
    LLM_API_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Embedding Configuration (Local)
    EMBEDDING_API_KEY: str = ""  # Not used for local embeddings
    EMBEDDING_MODEL: str = "Qwen/Qwen3-Embedding-0.6B"
    EMBEDDING_API_BASE_URL: str = "local"
    EMBEDDING_DIMENSION: int = 1024
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIR: str = "./uploads"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from environment
    )
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Convert MB to bytes for upload size validation."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


# Global settings instance
settings = Settings()
