from pydantic_settings import BaseSettings


class settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    class config:
        env_file = ".env"
        case_sensitive = False


app_settings = settings()

