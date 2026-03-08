import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_env: str
    log_level: str
    cors_allow_origins: list[str]
    mysql_host: str
    mysql_port: int
    mysql_db: str
    mysql_user: str
    mysql_password: str
    database_url: str | None
    model_gateway_provider: str
    model_gateway_api_key: str
    model_gateway_base_url: str
    model_gateway_model: str
    model_gateway_timeout_seconds: int

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )


def get_settings() -> Settings:
    _load_local_env_file()
    return Settings(
        app_env=os.getenv("APP_ENV", "local"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        cors_allow_origins=_parse_csv_env(
            os.getenv(
                "CORS_ALLOW_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173",
            )
        ),
        mysql_host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        mysql_port=int(os.getenv("MYSQL_PORT", "3307")),
        mysql_db=os.getenv("MYSQL_DB", "my_edu"),
        mysql_user=os.getenv("MYSQL_USER", "my_edu"),
        mysql_password=os.getenv("MYSQL_PASSWORD", "my_edu"),
        database_url=os.getenv("DATABASE_URL"),
        model_gateway_provider=os.getenv("MODEL_GATEWAY_PROVIDER", "mock").strip().lower(),
        model_gateway_api_key=os.getenv("MODEL_GATEWAY_API_KEY", "").strip(),
        model_gateway_base_url=os.getenv("MODEL_GATEWAY_BASE_URL", "https://api.deepseek.com").strip(),
        model_gateway_model=os.getenv("MODEL_GATEWAY_MODEL", "deepseek-chat").strip(),
        model_gateway_timeout_seconds=int(os.getenv("MODEL_GATEWAY_TIMEOUT_SECONDS", "10")),
    )


def _parse_csv_env(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _load_local_env_file() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


settings = get_settings()
