from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.config import get_settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"])


import hashlib
import secrets

settings = get_settings()
ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    salt = secrets.token_hex(32)
    pwdhash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 480000)
    return f"$pbkdf2-sha256$480000${salt}${pwdhash.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
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
