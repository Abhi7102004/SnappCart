import boto3
from botocore.exceptions import ClientError,NoCredentialsError
from loguru import logger
from typing import Optional

from app.core.config import settings
from app.core.email_templates import render_email

_ses_client = None

def _get_ses_client():
    global _ses_client
    if _ses_client is None:
        _ses_client=boto3.client(
            "ses",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
    return _ses_client
class EmailService:
    """
    Single interface for sending all emails.
    """
    
    def _send(to_email: str, subject: str, html_body: str, text_body: str) ->None:
        use_mock = settings.debug and not settings.aws_access_key_id
        
        if use_mock:
            logger.info(f"[MOCK EMAIL] To: {to_email}")
            logger.info(f"[MOCK EMAIL] Subject: {subject}")
            logger.info(f"[MOCK EMAIL] Preview: {text_body[:200]}")
            return
        
        try:
            client=_get_ses_client()
            client.send_email(
                Source=f"{settings.ses_from_name} <{settings.ses_from_email}>",
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Html": {"Data": html_body, "Charset": "UTF-8"},
                        "Text": {"Data": text_body, "Charset": "UTF-8"},
                    },
                },
            )
            logger.info(f"Email sent via SES: '{subject}' → {to_email}")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "MessageRejected":
                logger.error(
                    f"SES rejected email to {to_email} — likely sandbox mode "
                    f"restriction (recipient email not verified in SES)"
                )
            else:
                logger.error(f"SES error sending to {to_email}: {error_code}")
        except NoCredentialsError:
            logger.error("AWS credentials invalid or missing — email not sent")
    
    @staticmethod
    def send_verification_email(to_email:str,full_name:str | None,token:str) -> None:
        verify_link = f"{settings.frontend_url}/verify-email?token={token}"
        html_body = render_email("verify_email.html",full_name=full_name,verify_link=verify_link)
        text_body = (
            f"Hi {full_name or 'there'},\n\n"
            f"Verify your SnappCart email: {verify_link}\n\n"
            f"This link expires in 24 hours."
        )
        subject="Verify your SnappCart email"
        EmailService._send(to_email,subject,html_body,text_body)
        
    @staticmethod
    def send_password_reset_email(to_email: str, full_name: str | None, token: str) ->None:
        reset_link=f"{settings.frontend_url}/reset-password?token={token}"
        html_body = render_email("password_reset.html",full_name=full_name,reset_link=reset_link)
        text_body = (
            f"Hi {full_name or 'there'},\n\n"
            f"Verify your SnappCart email: {reset_link}\n\n"
            f"This link expires in 24 hours."
        )
        subject="Reset your SnappCart password"
        EmailService._send(to_email,subject,html_body,text_body)
        
                
