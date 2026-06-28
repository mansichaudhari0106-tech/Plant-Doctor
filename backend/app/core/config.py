import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./plant_doctor.db")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    VISION_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    TEXT_MODEL: str = "llama-3.3-70b-versatile"
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
settings = Settings()
