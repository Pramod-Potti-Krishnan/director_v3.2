"""
Settings configuration for Deckster.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    APP_ENV: str = Field("development", env="APP_ENV")
    DEBUG: bool = Field(True, env="DEBUG")
    LOG_LEVEL: str = Field("DEBUG", env="LOG_LEVEL")
    
    # API settings
    API_HOST: str = Field("0.0.0.0", env="API_HOST")
    API_PORT: int = Field(8000, env="PORT")
    
    # Supabase settings
    SUPABASE_URL: Optional[str] = Field(None, env="SUPABASE_URL")
    SUPABASE_ANON_KEY: Optional[str] = Field(None, env="SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY: Optional[str] = Field(None, env="SUPABASE_SERVICE_KEY")
    
    # AI services
    GOOGLE_API_KEY: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    # Logging
    LOGFIRE_TOKEN: Optional[str] = Field(None, env="LOGFIRE_TOKEN")
    
    # Streamlined WebSocket Protocol
    USE_STREAMLINED_PROTOCOL: bool = Field(
        default=True,
        description="Enable streamlined WebSocket message protocol"
    )
    
    STREAMLINED_PROTOCOL_PERCENTAGE: int = Field(
        default=100,
        ge=0,
        le=100,
        description="Percentage of sessions to use streamlined protocol (0-100)"
    )
    
    # Layout Architect Settings (Phase 2)
    LAYOUT_ARCHITECT_MODEL: str = Field("gemini-2.5-flash-lite-preview-06-17", env="LAYOUT_ARCHITECT_MODEL")
    LAYOUT_ARCHITECT_TEMPERATURE: float = Field(0.7, env="LAYOUT_ARCHITECT_TEMPERATURE")
    LAYOUT_GRID_WIDTH: int = Field(160, env="LAYOUT_GRID_WIDTH")
    LAYOUT_GRID_HEIGHT: int = Field(90, env="LAYOUT_GRID_HEIGHT")
    LAYOUT_MARGIN: int = Field(8, env="LAYOUT_MARGIN")
    LAYOUT_GUTTER: int = Field(4, env="LAYOUT_GUTTER")
    LAYOUT_WHITE_SPACE_MIN: float = Field(0.3, env="LAYOUT_WHITE_SPACE_MIN")
    LAYOUT_WHITE_SPACE_MAX: float = Field(0.5, env="LAYOUT_WHITE_SPACE_MAX")
    
    # Three-Agent Layout Architect Configuration (Phase 2 - New Architecture)
    THEME_AGENT_MODEL: str = Field("gemini-2.5-flash-lite-preview-06-17", env="THEME_AGENT_MODEL")
    STRUCTURE_AGENT_MODEL: str = Field("gemini-2.5-flash-lite-preview-06-17", env="STRUCTURE_AGENT_MODEL")
    LAYOUT_ENGINE_MODEL: str = Field("gemini-2.5-flash-lite-preview-06-17", env="LAYOUT_ENGINE_MODEL")
    
    # Phase 2B Content-Driven Architecture Configuration
    USE_PHASE_2B_ARCHITECTURE: bool = Field(True, env="USE_PHASE_2B_ARCHITECTURE")
    CONTENT_AGENT_MODEL: str = Field("gemini-2.5-flash-lite-preview-06-17", env="CONTENT_AGENT_MODEL")
    USE_LEGACY_WORKFLOW: bool = Field(False, env="USE_LEGACY_WORKFLOW")

    # v2.0: Deck-Builder Integration
    DECK_BUILDER_ENABLED: bool = Field(True, env="DECK_BUILDER_ENABLED")
    DECK_BUILDER_API_URL: str = Field("http://localhost:8000", env="DECK_BUILDER_API_URL")
    DECK_BUILDER_TIMEOUT: int = Field(30, env="DECK_BUILDER_TIMEOUT")

    # v3.1: Text Service Integration (Stage 6 - Content Generation)
    TEXT_SERVICE_ENABLED: bool = Field(True, env="TEXT_SERVICE_ENABLED")
    TEXT_SERVICE_URL: str = Field(
        "https://web-production-e3796.up.railway.app",
        env="TEXT_SERVICE_URL"
    )
    TEXT_SERVICE_TIMEOUT: int = Field(60, env="TEXT_SERVICE_TIMEOUT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env
    
    @property
    def has_ai_key(self) -> bool:
        """Check if at least one AI API key is configured."""
        return bool(self.GOOGLE_API_KEY or self.OPENAI_API_KEY or self.ANTHROPIC_API_KEY)
    
    def validate_settings(self) -> None:
        """Validate that essential settings are configured."""
        if not self.has_ai_key:
            raise ValueError(
                "At least one AI API key must be configured. "
                "Set GOOGLE_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY in your .env file."
            )


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# For backward compatibility with existing code
settings = get_settings()