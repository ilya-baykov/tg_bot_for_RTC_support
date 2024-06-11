from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL(self):
        # DSN: f"postgresql+psycopg://postgres:postgres@localhost:5432/telegram-db"
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file="C:/Users/ilyab/PycharmProjects/Tg_bot_01/Tg_Bot/bot/database/.env")


settings = Settings()
