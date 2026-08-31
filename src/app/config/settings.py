from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

    project_name: str = "Agents Network"
    version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    database_url : str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-20b"


@lru_cache
def get_settings() -> Settings:
    return Settings()
