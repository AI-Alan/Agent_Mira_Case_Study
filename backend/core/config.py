from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    OPENAI_API_KEY: str
    DATABASE_NAME: str = "agent_mira"

    class Config:
        env_file = ".env"

settings = Settings()
