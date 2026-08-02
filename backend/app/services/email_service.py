from loguru import logger
from app.core.config import settings

class EmailService:
    """
    Single interface for sending all emails.

    Right now: mock (logs to console in dev).
    Day 27: swap the internals to use boto3 + AWS SES.
    Callers (AuthService etc.) never change — same method
    signatures, just the implementation inside changes.
    """
    
    @staticmethod
    def send_verification_email(to_email:str,full_name:str | None,token:str) -> None:
        verify_link = f"{settings.frontend_url}/verify-email?token={token}"
        
        if settings.debug:
            logger.info(f"[MOCK EMAIL] To: {to_email}")
            logger.info(f"[MOCK EMAIL] Subject: Verify your SnappCart email")
            logger.info(f"[MOCK EMAIL] Link: {verify_link}")
        else:
            logger.warning("AWS SES not yet configured — email not sent")

    @staticmethod
    def send_password_reset_email(to_email: str, full_name: str | None, token: str) ->None:
        reset_link=f"{settings.frontend_url}/reset-password?token={token}"
        
        if settings.debug:
            logger.info(f"[MOCK EMAIL] To: {to_email}")
            logger.info(f"[MOCK EMAIL] Subject: Reset your SnappCart password")
            logger.info(f"[MOCK EMAIL] Link: {reset_link}")
        else:
            logger.warning("AWS SES not yet configured — email not sent")
        
                
