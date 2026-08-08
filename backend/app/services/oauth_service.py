import secrets
import httpx
from urllib.parse import urlencode
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response
from loguru import logger

from app.core.config import settings
from app.core.constants import OAUTH_STATE_PREFIX, OAUTH_STATE_TTL_SECONDS
from app.core import messages as msg
from app.core.redis import redis_client
from app.core.security.jwt import create_access_token, create_refresh_token, get_refresh_token_key
from app.models.user import User, UserRole, OAuthProvider
from app.schemas.user import UserResponse
from app.schemas.auth import LoginResponse
from app.services.auth_service import AuthService

class OAuthService:
    
    # ── State Parameter (CSRF prevention, shared by both providers) ──
    
    @staticmethod
    async def generate_state() ->str:
        state = secrets.token_urlsafe(24)
        await redis_client.setex(f"{OAUTH_STATE_PREFIX}{state}",OAUTH_STATE_TTL_SECONDS,"1")
        return state
    
    @staticmethod
    async def verify_state(state: str) -> None:
        key=f"{OAUTH_STATE_PREFIX}{state}"
        exists=await redis_client.get(key)
        if not exists:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, msg.OAUTH_STATE_INVALID)
        await redis_client.delete(key)

    # ── Shared: find-or-create user + issue SnappCart tokens ─────────
    
    @staticmethod
    async def _login_or_create_user(
        db:Session,
        response:Response,
        provider:OAuthProvider,
        provider_id:str,
        email:str,
        full_name:str,
        avatar_url:str
    ) -> LoginResponse:
        
        provider_field = User.google_id if provider==OAuthProvider.google else User.github_id
        
        user = db.query(User).filter(provider_field==provider_id,User.is_deleted==False).first()
        
        if not user:
            user = db.query(User).filter(User.email == email,User.is_deleted==False).first()
            
            if user:
                if provider==OAuthProvider.google:
                    user.google_id=provider_id
                elif provider==OAuthProvider.github:
                    user.github_id=provider_id
                if not user.oauth_avatar_url and avatar_url:
                    user.oauth_avatar_url = avatar_url

                db.commit()
                logger.info(f"Linked {provider.value} to existing account: {email}")
            else:
                user = User(
                    email=email,
                    full_name=full_name,
                    hashed_password=None,
                    role=UserRole.customer,
                    oauth_provider=provider,
                    google_id=provider_id if provider == OAuthProvider.google else None,
                    github_id=provider_id if provider == OAuthProvider.github else None,
                    oauth_avatar_url=avatar_url,
                    is_email_verified=True,
                    is_phone_verified=False,
                    is_active=True,
                    is_deleted=False,
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info(f"New {provider.value} user created: {email}")

        access_token = create_access_token(str(user.id), user.role.value)
        refresh_token = create_refresh_token(str(user.id))
        
        await AuthService._store_refresh_token(str(user.id), refresh_token)
        AuthService._set_refresh_cookie(response,refresh_token)
        
        user.last_login_at = user.last_login_at  # no-op placeholder for clarity
        db.commit()
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    # ── GOOGLE ─────────────────────────────────────────────────────
    
    @staticmethod
    async def get_google_authorization_url() -> str:
        state = await OAuthService.generate_state()
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    @staticmethod
    async def handle_google_callback(
        code:str,state:str,db:Session,response:Response
    ) ->LoginResponse:
        await OAuthService.verify_state(state)
        
        async with httpx.AsyncClient() as client:
            token_res=await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            
            if token_res.status_code != 200:
                logger.error(f"Google token exchange failed: {token_res.text}")
                raise HTTPException(status.HTTP_400_BAD_REQUEST, msg.OAUTH_FAILED)
            
            google_access_token = token_res.json()["access_token"]
            
            profile_res = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {google_access_token}"},
            )
            
            if profile_res.status_code!=200:
                logger.error(f"Google profile fetch failed: {profile_res.text}")
                raise HTTPException(status.HTTP_400_BAD_REQUEST, msg.OAUTH_FAILED)
            
            profile = profile_res.json()
            
            return await OAuthService._login_or_create_user(
                db=db,
                response=response,
                provider=OAuthProvider.google,
                provider_id=profile["id"],
                email=profile["email"],
                full_name=profile.get("name"),
                avatar_url=profile.get("picture"),
            )
    
    # ── GITHUB ─────────────────────────────────────────────────────
    
    @staticmethod
    async def get_github_authorization_url() -> str:
        state = await OAuthService.generate_state()
        params = {
            "client_id": settings.github_client_id,
            "redirect_uri": settings.github_redirect_uri,
            "scope": "read:user user:email",
            "state": state,
        }
        return f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    
    @staticmethod
    async def handle_github_callback(
        code:str,state:str,db:Session,response:Response
    ) ->LoginResponse:
        
        await OAuthService.verify_state((state))
        
        async with httpx.AsyncClient() as client:
            
            token_res=await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "code": code,
                    "client_id": settings.github_client_id,
                    "client_secret": settings.github_client_secret,
                    "redirect_uri": settings.github_redirect_uri,
                },
                headers={
                    "Accept": "application/json"
                }
            )
            
            if token_res.status_code != 200:
                logger.error(f"GitHub token exchange failed: {token_res.text}")
                raise HTTPException(status.HTTP_400_BAD_REQUEST, msg.OAUTH_FAILED)

            token_data = token_res.json()
            if "access_token" not in token_data:
                logger.error(f"GitHub token exchange rejected: {token_data}")
                raise HTTPException(status.HTTP_400_BAD_REQUEST, msg.OAUTH_FAILED)
            
            github_access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {github_access_token}"}
            
            profile_res=await client.get("https://api.github.com/user",headers=headers)
            
            if profile_res.status_code != 200:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, msg.OAUTH_FAILED)
            
            profile = profile_res.json()
            
            emails_res = await client.get("https://api.github.com/user/emails", headers=headers)
            if emails_res.status_code != 200:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, msg.OAUTH_FAILED)
            
            emails=emails_res.json()
            
            primary_email = next(
                (e["email"] for e in emails if e.get("primary") and e.get("verified")),
                None
            )
            
            if not primary_email:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    "No verified primary email found on your GitHub account"
                )

            return await OAuthService._login_or_create_user(
                db=db,
                response=response,
                provider=OAuthProvider.github,
                provider_id=str(profile["id"]),
                email=primary_email,
                full_name=profile.get("name") or profile.get("login"),
                avatar_url=profile.get("avatar_url"),
            )




        
