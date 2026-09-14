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
    
    # LLM Configuration
    LLM_API_KEY: str = "test-key"  # Default for testing
    LLM_MODEL: str = "gpt-4"
    LLM_API_BASE_URL: str = "https://api.openai.com/v1"
    
    # Embedding Configuration
    EMBEDDING_API_KEY: str = "test-key"  # Default for testing
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    EMBEDDING_API_BASE_URL: str = "https://api.openai.com/v1"
    EMBEDDING_DIMENSION: int = 1536
    
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
