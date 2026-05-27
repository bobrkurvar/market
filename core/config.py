import json

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    redis_host: str
    test_db_name: str
    is_test: bool = False

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def test_db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.test_db_name}"


def load_config() -> Settings:
    conf = Settings()  # type: ignore
    return conf
