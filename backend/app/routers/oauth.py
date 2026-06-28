from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.models import User
from app.models.schemas import Token, SupabaseTokenRequest

router = APIRouter(prefix="/auth", tags=["oauth"])


@router.get("/google/url")
def google_login_url():
    """Returns the Supabase Google OAuth URL."""
    if not settings.SUPABASE_URL:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    redirect_to = f"{settings.FRONTEND_URL}?oauth_callback=1"
    url = (
        f"{settings.SUPABASE_URL}/auth/v1/authorize"
        f"?provider=google"
        f"&redirect_to={redirect_to}"
    )
    return {"url": url}


@router.post("/google/callback", response_model=Token)
def google_callback(payload: SupabaseTokenRequest, db: Session = Depends(get_db)):
    """
    Streamlit sends the Supabase access_token it received from the OAuth redirect.
    We verify it against the Supabase JWT secret, find-or-create the user, 
    and return our own app JWT.
    """
    try:
        data = jwt.decode(
            payload.supabase_access_token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Supabase token: {e}")

    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="No email found in token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, hashed_password="oauth-google", auth_provider="google")
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token)


@router.get("/oauth/callback", response_class=HTMLResponse)
def oauth_callback_page():
    """
    Supabase redirects here after Google login with #access_token=... in the URL fragment.
    Fragments are not sent to servers, so we use JS to read it and pass it to Streamlit
    via query params.
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Logging you in...</title></head>
    <body>
        <p style="font-family:sans-serif;text-align:center;margin-top:80px;color:#2D6A4F">
            🌿 Logging you in...
        </p>
        <script>
            // Supabase puts the tokens in the URL hash fragment
            const hash = window.location.hash.substring(1);
            const params = new URLSearchParams(hash);
            const accessToken = params.get('access_token');

            if (accessToken) {{
                // Redirect to Streamlit with the token as a query param
                const streamlitUrl = '{settings.FRONTEND_URL}';
                window.location.href = streamlitUrl + '?access_token=' + encodeURIComponent(accessToken) + '&oauth_callback=1';
            }} else {{
                document.body.innerHTML += '<p style="color:red;text-align:center">Login failed. No token received.</p>';
            }}
        </script>
    </body>
    </html>
    """
    return html
