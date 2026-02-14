from datetime import UTC, datetime, timedelta


import hashlib
import secrets

from jose import jwt
from app.config import get_settings

import hashlib
import secrets

# try to import bcrypt at module import time for legacy hashes
try:
    import bcrypt as _bcrypt_module
except Exception:
    _bcrypt_module = None

settings = get_settings()
ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    salt = secrets.token_hex(32)
    pwdhash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 480000)
    return f"$pbkdf2-sha256$480000${salt}${pwdhash.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Support legacy bcrypt hashes (start with $2b$ or $2a$) and new pbkdf2 format
    if not hashed_password:
        return False
    if hashed_password.startswith("$2"):
        if _bcrypt_module is None:
            return False
        try:
            return _bcrypt_module.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False
    try:
        parts = hashed_password.split("$")
        if len(parts) != 5 or parts[1] != "pbkdf2-sha256":
            return False
        iterations = int(parts[2])
        salt = parts[3]
        expected_hash = parts[4]
        pwdhash = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), iterations)
        return pwdhash.hex() == expected_hash
    except (IndexError, ValueError):
        return False


def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": subject, "role": role, "exp": expire}, settings.secret_key, algorithm=ALGORITHM)
