from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.schemas.oauth import OAuthURLResponse
from app.services.oauth_service import OAuthService

router = APIRouter(prefix="/auth", tags=["OAuth"])

# ── GOOGLE ─────────────────────────────────────────────────────────

@router.get("/google/login", response_model=OAuthURLResponse)
async def google_login():
    """Frontend calls this to GET the URL, then redirects the browser to it."""
    url = await OAuthService.get_google_authorization_url()
    return OAuthURLResponse(authorization_url=url)

@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),         #Query(...) means in url params code,state is present and ... ensures it's required field
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    """
    Google redirects here after user consents.
    """
    response = RedirectResponse(url=settings.frontend_url)
    result = await OAuthService.handle_google_callback(code, state, db, response)

    redirect_url = f"{settings.frontend_url}/oauth/callback#access_token={result.access_token}"
    response.headers["location"] = redirect_url
    return response

# ── GITHUB ─────────────────────────────────────────────────────────

@router.get("/github/login", response_model=OAuthURLResponse)
async def github_login():
    url = await OAuthService.get_github_authorization_url()
    return OAuthURLResponse(authorization_url=url)

@router.get("/github/callback")
async def github_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    response = RedirectResponse(url=settings.frontend_url)
    result = await OAuthService.handle_github_callback(code, state, db, response)

    redirect_url = f"{settings.frontend_url}/oauth/callback#access_token={result.access_token}"
    response.headers["location"] = redirect_url
    return response