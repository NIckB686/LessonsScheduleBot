from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class BotConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="tg_bot_")

    token: SecretStr
    drop_pending_updates: bool = True
    use_webhook: bool = False


class WebAppConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="webapp_")

    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8080


class WebhookConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="webhook_")

    base_url: str = ""
    path: str = "/webhook"
    secret: SecretStr = SecretStr("")

    @computed_field
    @property
    def url(self) -> str:
        """Полный URL вебхука."""
        return f"{self.base_url}{self.path}"


class TelegramConfig(ConfigBase):
    bot: BotConfig = Field(default_factory=BotConfig)
    webapp: WebAppConfig = Field(default_factory=WebAppConfig)
    webhook: WebhookConfig = Field(default_factory=WebhookConfig)


class PostgresConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="postgres_")

    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    DB: str

    @computed_field
    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"


class RedisConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="redis_")

    host: str
    port: int
    database: int
    password: SecretStr
    username: str


class Config(BaseSettings):
    tg: TelegramConfig = Field(default_factory=TelegramConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)

    @classmethod
    def load(cls) -> Config:
        return cls()
