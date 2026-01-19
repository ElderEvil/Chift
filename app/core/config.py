from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Odoo Configuration
    odoo_url: str
    odoo_db: str
    odoo_username: str
    odoo_password: str

    # Database Configuration
    database_url: str

    # Sync Configuration
    sync_interval_minutes: int = 15

    # API Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API Configuration
    api_v1_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False, env_nested_delimiter="__"
    )


settings = Settings()
