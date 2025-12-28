from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class BotConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="tg_bot_")

    token: SecretStr
    drop_pending_update: bool = True


class WebAppConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="webapp_")

    host: str
    port: int


class WebhookConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="webhook_")

    base_url: str
    path: str

    @computed_field
    @property
    def url(self) -> str:
        """Полный URL вебхука."""
        return f"{self.base_url}{self.path}"


class TelegramConfig(ConfigBase):
    bot: BotConfig = Field(default_factory=BotConfig)
    webapp: WebAppConfig = Field(default_factory=WebAppConfig)
    webhook: WebhookConfig = Field(default_factory=WebhookConfig)


class Config(BaseSettings):
    """Класс, читающий настройки из переменных окружения и .env файла."""

    tg: TelegramConfig = Field(default_factory=TelegramConfig)

    @classmethod
    def load(cls) -> "Config":
        return cls()
