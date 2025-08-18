from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the application."""

    host: str = Field(
        default="localhost",
        description="Host to bind the server to",
    )

    log_level: str = Field(
        default="DEBUG",
        description="Logging level for the application",
    )

    port: int = Field(
        default=8000,
        description="Port to bind the server to",
    )

    static_files_path: str = Field(
        default="app",
        description="Path to the static files directory",
    )

    model_config = SettingsConfigDict(extra="ignore")


settings = Settings()
