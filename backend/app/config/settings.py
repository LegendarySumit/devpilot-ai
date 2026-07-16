from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "DevPilot AI"
    api_version: str = "v1"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/devpilot"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
