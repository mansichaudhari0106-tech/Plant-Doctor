from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.models import User
from app.models.schemas import Token, SupabaseTokenRequest

router = APIRouter(prefix="/auth", tags=["oauth"])


@router.get("/google/url")
def google_login_url():
    if not settings.SUPABASE_URL:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    redirect_to = f"{settings.BACKEND_URL}/auth/oauth/callback"
    url = (
        f"{settings.SUPABASE_URL}/auth/v1/authorize"
        f"?provider=google"
        f"&redirect_to={redirect_to}"
    )
    return {"url": url, "redirect_to": redirect_to}


@router.post("/google/callback", response_model=Token)
def google_callback(payload: SupabaseTokenRequest, db: Session = Depends(get_db)):
    """
    Verify the Supabase access token by calling Supabase's /auth/v1/user endpoint.
    This works regardless of JWT algorithm (HS256 or ES256).
    """
    try:
        response = httpx.get(
            f"{settings.SUPABASE_URL}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {payload.supabase_access_token}",
                "apikey": settings.SUPABASE_ANON_KEY,
            },
            timeout=10,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to contact Supabase: {e}")

    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid Supabase token: {response.text}"
        )

    user_data = response.json()
    email = user_data.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="No email found in Supabase user")

    # Find or create user in our database
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
    Supabase redirects here after Google login.
    Reads the access_token from URL fragment and forwards to Streamlit.
    """
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Logging you in...</title>
    <style>
        body {{ font-family: sans-serif; text-align: center; margin-top: 80px; color: #2D6A4F; }}
    </style>
</head>
<body>
    <p style="font-size:48px">🌿</p>
    <p>Logging you in with Google...</p>
    <script>
        const hash = window.location.hash.substring(1);
        const params = new URLSearchParams(hash);
        const accessToken = params.get('access_token');
        const error = params.get('error_description') || params.get('error');

        if (accessToken) {{
            window.location.href = '{settings.FRONTEND_URL}?access_token=' + encodeURIComponent(accessToken) + '&oauth_callback=1';
        }} else if (error) {{
            document.body.innerHTML += '<p style="color:red">Error: ' + error + '</p>';
        }} else {{
            const qParams = new URLSearchParams(window.location.search);
            const qToken = qParams.get('access_token');
            if (qToken) {{
                window.location.href = '{settings.FRONTEND_URL}?access_token=' + encodeURIComponent(qToken) + '&oauth_callback=1';
            }} else {{
                document.body.innerHTML += '<p style="color:red">No token received.</p>';
                document.body.innerHTML += '<pre style="font-size:11px;text-align:left;margin:20px auto;max-width:600px;background:#f5f5f5;padding:12px">'
                    + 'Hash: ' + window.location.hash + '\\n'
                    + 'Search: ' + window.location.search + '</pre>';
            }}
        }}
    </script>
</body>
</html>"""
    return html
