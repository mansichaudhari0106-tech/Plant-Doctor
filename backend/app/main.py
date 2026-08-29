import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import Base, engine
from app.core.config import settings
from app.routers import auth, plants, diagnosis, oauth, photos

# Create all tables
Base.metadata.create_all(bind=engine)

# Safe migration: add auth_provider column if missing
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN auth_provider VARCHAR"))
        conn.execute(text("UPDATE users SET auth_provider = 'email' WHERE auth_provider IS NULL"))
        conn.commit()
    except Exception:
        pass  # Column already exists

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Plant Doctor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NOTE: /uploads static mount removed — photos now served privately via /photos/{id}
app.include_router(auth.router)
app.include_router(oauth.router)
app.include_router(plants.router)
app.include_router(diagnosis.router)
app.include_router(photos.router)

@app.get("/")
def root():
    return {"status": "ok", "service": "plant-doctor-api"}
