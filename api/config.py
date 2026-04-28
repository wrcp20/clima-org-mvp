from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    admin_api_key: str = "change-me"
    database_url: str = "sqlite:////app/data/clima.db"
    api_url: str = "http://api:8000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
