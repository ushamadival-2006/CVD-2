from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./cvd.db"
    SECRET_KEY: str = "changeme_min32chars_production_key!!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    MODEL_PATH: str = "../../data/processed/best_model.pkl"
    SCALER_PATH: str = "../../data/processed/scaler.pkl"
    RETINAL_MODEL_PATH: str = "../../models/retinal/hybrid_model.pth"
    UPLOAD_DIR: str = "uploads/"
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
