from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Класс, читающий настройки из переменных окружения и .env файла."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Bot settings
    tg_bot_token: SecretStr
    tg_bot_drop_pending_updates: bool = True

    # Webapp settings
    webapp_host: str
    webapp_port: int

    # Webhook settings
    webhook_base_url: str
    webhook_path: str

    @computed_field
    def webhook_url(self) -> str:
        """Полный URL вебхука."""
        return f"{self.webhook_base_url}{self.webhook_path}"


settings = Settings()
