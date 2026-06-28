from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from supabase import create_client
from jose import jwt, JWTError

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.models import User
from app.models.schemas import Token
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["oauth"])

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


class SupabaseTokenRequest(BaseModel):
    supabase_access_token: str


@router.get("/google/url")
def google_login_url():
    """Returns the Supabase Google OAuth URL for the frontend to redirect to."""
    res = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {
            "redirect_to": settings.FRONTEND_URL + "/oauth/callback"
        }
    })
    return {"url": res.url}


@router.post("/google/callback", response_model=Token)
def google_callback(payload: SupabaseTokenRequest, db: Session = Depends(get_db)):
    """
    Frontend sends the Supabase access token it received after Google OAuth.
    We verify it, find-or-create the user in our DB, return our own JWT.
    """
    try:
        # Verify the Supabase JWT using the JWT secret
        data = jwt.decode(
            payload.supabase_access_token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Supabase token")

    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="No email in token")

    # Find or create user (no password needed for OAuth users)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, hashed_password="oauth-google")
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token)
