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
    Works regardless of JWT algorithm (HS256 or ES256).
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise HTTPException(status_code=503,
                            detail="Supabase not configured on server")

    if not payload.supabase_access_token:
        raise HTTPException(status_code=400, detail="No access token provided")

    # Ask Supabase to verify its own token
    try:
        with httpx.Client(timeout=15) as client:
            response = client.get(
                f"{settings.SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {payload.supabase_access_token}",
                    "apikey": settings.SUPABASE_ANON_KEY,
                },
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Supabase request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Could not reach Supabase: {str(e)}")

    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail=f"Supabase rejected token (status {response.status_code}): {response.text[:200]}"
        )

    try:
        user_data = response.json()
    except Exception:
        raise HTTPException(status_code=502,
                            detail=f"Invalid response from Supabase: {response.text[:200]}")

    email = user_data.get("email")
    if not email:
        raise HTTPException(status_code=400,
                            detail=f"No email in Supabase response: {user_data}")

    # Find or create user in our DB
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
            window.location.href = '{settings.FRONTEND_URL}?access_token='
                + encodeURIComponent(accessToken) + '&oauth_callback=1';
        }} else if (error) {{
            document.body.innerHTML += '<p style="color:red">Error: ' + error + '</p>';
        }} else {{
            const qParams = new URLSearchParams(window.location.search);
            const qToken = qParams.get('access_token');
            if (qToken) {{
                window.location.href = '{settings.FRONTEND_URL}?access_token='
                    + encodeURIComponent(qToken) + '&oauth_callback=1';
            }} else {{
                document.body.innerHTML += '<p style="color:red">No token received from Google.</p>';
                document.body.innerHTML += '<pre style="font-size:11px;text-align:left;margin:20px auto;'
                    + 'max-width:600px;background:#f5f5f5;padding:12px">'
                    + 'Hash: ' + window.location.hash + '\\n'
                    + 'Search: ' + window.location.search + '</pre>';
            }}
        }}
    </script>
</body>
</html>"""
    return html
