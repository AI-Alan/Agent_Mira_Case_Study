from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    MONGO_URI: str
    OPENAI_API_KEY: Optional[str] = None  # Optional for now, required only for chat features
    GEMINI_API_KEY: Optional[str] = None  # Gemini API key for enhanced chat
    DATABASE_NAME: str = "agent_mira"
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # Ignore extra fields in .env file
    )

settings = Settings()
