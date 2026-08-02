from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

DUMMY_HASH = pwd_context.hash("dummy_password_for_timing")

def hash_password(password:str) -> str:
    """Hash password with bcrypt (salt auto-generated)"""
    return pwd_context.hash(password)

def verify_password(plain_password:str , hashed_password:str) -> bool:
    """
    Constant-time comparison — prevents timing attacks.
    """
    return pwd_context.verify(plain_password,hashed_password)
