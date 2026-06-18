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
    secret_key: str
    algorithm: str
    pepper: str
    image_service_port: str
    image_service_host: str

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def image_api_url(self):
        return f"http://{self.image_service_host}:{self.image_service_port}/"

    @property
    def test_db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.test_db_name}"

    @property
    def redis_url(self):
        return f"redis://{self.redis_host}:6379/0"


def load_config() -> Settings:
    conf = Settings()  # type: ignore
    return conf
