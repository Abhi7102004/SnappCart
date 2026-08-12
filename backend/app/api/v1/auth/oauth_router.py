# app/api/v1/auth/oauth_router.py

from fastapi import APIRouter, Depends, Query, Response, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.config import settings
from app.schemas.oauth import OAuthURLResponse
from app.services.oauth_service import OAuthService

router = APIRouter(prefix="/auth", tags=["OAuth"])


@router.get("/google/login", response_model=OAuthURLResponse)
async def google_login():
    url = await OAuthService.get_google_authorization_url()
    return OAuthURLResponse(authorization_url=url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None),
    db: Session = Depends(get_db),
):
    if error:
        return RedirectResponse(url=f"{settings.frontend_url}/oauth/callback?error={error}")

    if not code or not state:
        return RedirectResponse(url=f"{settings.frontend_url}/oauth/callback?error=missing_params")

    response = RedirectResponse(url=settings.frontend_url)
    try:
        result = await OAuthService.handle_google_callback(code, state, db, response)
    except Exception:
        logger.exception("Google OAuth callback failed")
        return RedirectResponse(url=f"{settings.frontend_url}/oauth/callback?error=oauth_failed")

    redirect_url = f"{settings.frontend_url}/oauth/callback#access_token={result.access_token}"
    response.headers["location"] = redirect_url
    return response


@router.get("/github/login", response_model=OAuthURLResponse)
async def github_login():
    url = await OAuthService.get_github_authorization_url()
    return OAuthURLResponse(authorization_url=url)


@router.get("/github/callback")
async def github_callback(
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None),
    db: Session = Depends(get_db),
):
    if error:
        return RedirectResponse(url=f"{settings.frontend_url}/oauth/callback?error={error}")

    if not code or not state:
        return RedirectResponse(url=f"{settings.frontend_url}/oauth/callback?error=missing_params")

    response = RedirectResponse(url=settings.frontend_url)
    try:
        result = await OAuthService.handle_github_callback(code, state, db, response)
    except Exception:
        logger.exception("GitHub OAuth callback failed")
        return RedirectResponse(url=f"{settings.frontend_url}/oauth/callback?error=oauth_failed")

    redirect_url = f"{settings.frontend_url}/oauth/callback#access_token={result.access_token}"
    response.headers["location"] = redirect_url
    return response