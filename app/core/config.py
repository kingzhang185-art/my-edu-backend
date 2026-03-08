import os
from dataclasses import dataclass


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

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )


def get_settings() -> Settings:
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
    )


def _parse_csv_env(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


settings = get_settings()
