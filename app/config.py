from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+asyncpg://blog_user:blog_password"
        "@localhost:5432/blog_db"
    )
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 300
    test_database_url: str = (
        "postgresql+asyncpg://blog_user:blog_password"
        "@localhost:5432/blog_db_test"
    )

    model_config = {"env_file": ".env"}


settings = Settings()
