"""Configuration settings for ScopeWise."""


from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Database Configuration
    database_url: str = "postgresql+psycopg://scopewise:scopewise@localhost:5433/scopewise"
    
    # Application Configuration
    app_name: str = "ScopeWise"
    debug: bool = False
    
    # Authentication Configuration
    jwt_secret_key: SecretStr = Field(min_length=32)  # noqa: F821
    token_expiry_hours: int = 24
    
    # Environment Configuration
    env: str = "local"
    
    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    
    # OpenRouter Configuration
    openrouter_api_key: str | None = None
    openrouter_model: str = "openai/gpt-4"
    openrouter_temperature: float = 0.0
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_timeout: int = Field(
        default=60,
        description="Per-request HTTP timeout in seconds (converted to ms for OpenRouter).",
    )
    openrouter_max_retries: int = 3
    
    # OpenAI Configuration (for direct OpenAI usage - optional, we use OpenRouter)
    openai_api_key: SecretStr | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    
    # Note: Embeddings now use OpenRouter (configured via openrouter_api_key above)
    # This supports models like: openai/text-embedding-3-small
    
    # Tavily Configuration (for web search in market research)
    tavily_api_key: SecretStr | None = None
    
    # ChromaDB Configuration (for vector store)
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "firm_projects"
    
    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


def get_settings() -> Settings:
    return Settings(jwt_secret_key=SecretStr("default-secret-key-change-in-production"))
