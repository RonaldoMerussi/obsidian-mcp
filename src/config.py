from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    vault_path: Path
    mcp_auth_token: str
    git_remote: str = "origin"
    git_author: str = "MCP Bot <mcp@bot>"
    sync_pull_interval: int = 300
    allow_destructive: bool = False
    port: int = 8000
    allowed_host: str


settings = Settings()
