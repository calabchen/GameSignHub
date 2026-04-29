"""密码认证 + JWT 管理."""

from datetime import UTC, datetime, timedelta

import bcrypt

from app.config import get_settings

JWT_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token() -> str:
    from jose import jwt as jose_jwt

    settings = get_settings()
    secret = settings.secret_key.encode() if settings.secret_key else _get_or_create_secret_key()

    expire = datetime.now(UTC) + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jose_jwt.encode(payload, secret, algorithm="HS256")


def verify_access_token(token: str) -> dict:
    from jose import jwt as jose_jwt
    from jose.exceptions import JWTError

    settings = get_settings()
    secret = settings.secret_key.encode() if settings.secret_key else _get_or_create_secret_key()

    return jose_jwt.decode(token, secret, algorithms=["HS256"])


def _get_or_create_secret_key() -> bytes:
    settings = get_settings()
    if not settings.secret_key:
        import secrets
        new_key = secrets.token_hex(32)
        settings.secret_key = new_key
    return settings.secret_key.encode()
