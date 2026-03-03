from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_DETAILS: str
    API_KEY: str = "default_secret_key"

    class Config:
        env_file = ".env"

settings = Settings()
