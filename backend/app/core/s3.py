import boto3
from botocore.exceptions import ClientError
from loguru import logger

from app.core.config import settings

s3_client = boto3.client(
    "s3",
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)

def check_s3_connection() -> bool:
    """
    Health check — head_bucket is a very lightweight API call that just asks "does this bucket exist and can I access it?
    """
    try:
        s3_client.head_bucket(Bucket=settings.s3_bucket)
        logger.info(f"S3 bucket '{settings.s3_bucket}': OK ✅")
        return True
    except ClientError as e:
        logger.error(f"S3 bucket check failed: {e}")
        return False