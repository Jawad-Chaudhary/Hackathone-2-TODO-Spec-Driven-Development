# [Task T004] Backend environment configuration with Pydantic validation

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application configuration with environment variable validation."""

    database_url: str = Field(..., description="PostgreSQL connection string")
    better_auth_secret: str = Field(..., description="JWT signing secret (must match frontend)")
    cors_origins: str = Field(..., description="Comma-separated list of allowed origins")
    frontend_url: str = Field(default="http://localhost:3000", description="Frontend URL for CORS configuration")
    environment: str = Field(default="development", description="Environment: development or production")
    log_level: str = Field(default="INFO", description="Logging level")

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS into a list of strings."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @field_validator("better_auth_secret")
    @classmethod
    def validate_secret_length(cls, v: str) -> str:
        """Ensure BETTER_AUTH_SECRET is sufficiently long for security."""
        if len(v) < 32:
            raise ValueError("BETTER_AUTH_SECRET must be at least 32 characters for security")
        return v

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()
