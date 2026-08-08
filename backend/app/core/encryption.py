import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.core.config import settings

_fernet: Fernet | None = None

def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        # Derive a 32-byte Fernet key from settings.secret_key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"snappcart_2fa",
            iterations=100_000,
        )
        key = base64.urlsafe_b64encode(
            kdf.derive(settings.secret_key.encode())
        )
        _fernet = Fernet(key)
    return _fernet

def encrypt(plaintext: str) -> str:
    """Encrypt a string. Returns base64-encoded ciphertext."""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a string encrypted by encrypt(). Raises on invalid ciphertext."""
    return _get_fernet().decrypt(ciphertext.encode()).decode()