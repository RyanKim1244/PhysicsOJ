"""Google OAuth authentication router."""

import json
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, BASE_URL
from app.database import get_db
from app.models.models import User

router = APIRouter(tags=["auth"])

# Google OAuth setup
oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Get logged-in user from session. Returns None if not logged in."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def require_login(request: Request, db: Session = Depends(get_db)) -> User:
    """Require logged-in user. Raises 401 if not authenticated."""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    return user


@router.get("/auth/login")
async def login(request: Request):
    """Redirect to Google login page."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth가 설정되지 않았습니다. .env 파일을 확인하세요.")
    redirect_uri = BASE_URL + "/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback."""
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception:
        return RedirectResponse(url="/#login-error")

    userinfo = token.get("userinfo")
    if not userinfo:
        return RedirectResponse(url="/#login-error")

    google_id = userinfo["sub"]
    email = userinfo.get("email", "")
    name = userinfo.get("name", email.split("@")[0])
    picture = userinfo.get("picture", "")

    # Find or create user
    user = db.query(User).filter(User.google_id == google_id).first()
    if not user:
        # Check email conflict
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.google_id = google_id
            user.picture = picture
            user.display_name = name
        else:
            # Create new user - username from email prefix
            base_username = email.split("@")[0] if email else f"user_{google_id[:8]}"
            username = base_username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1

            user = User(
                username=username,
                display_name=name,
                email=email,
                picture=picture,
                google_id=google_id,
            )
            db.add(user)
    else:
        user.display_name = name
        user.picture = picture

    db.commit()
    db.refresh(user)

    # Save to session
    request.session["user_id"] = user.id
    request.session["username"] = user.username

    return RedirectResponse(url="/")


@router.get("/auth/logout")
async def logout(request: Request):
    """Clear session and redirect to home."""
    request.session.clear()
    return RedirectResponse(url="/")


@router.get("/auth/me")
async def get_me(request: Request, db: Session = Depends(get_db)):
    """Get current logged-in user info."""
    user = get_current_user(request, db)
    if not user:
        return {"logged_in": False}
    return {
        "logged_in": True,
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "email": user.email or "",
        "picture": user.picture or "",
    }
