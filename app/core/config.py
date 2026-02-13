from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "Projeto Back End - Lanchonete"
    SECRET_KEY: str = "troque-essa-chave-em-producao"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    DATABASE_URL: str = "sqlite:///./app.db"


settings = Settings()
