"""密码认证 + 密钥派生 + JWT 管理."""

import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
from argon2.low_level import hash_secret_raw, Type

from app.config import get_settings

# Argon2id 参数
ARGON2_TIME_COST = 3
ARGON2_MEM_COST = 64 * 1024  # 64 MB
ARGON2_PARALLELISM = 4
ARGON2_KEY_LENGTH = 32  # 256-bit for AES-256
ARGON2_SALT = b"GameSignHub-Argon2id-Salt-v1"  # 固定 salt，仅用于密钥派生

# JWT 过期时间
JWT_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    """bcrypt 哈希密码，用于存储验证."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """验证密码是否匹配 bcrypt 哈希."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def derive_encryption_key(password: str) -> bytes:
    """Argon2id 派生 256-bit 加密密钥.

    此密钥仅用于 AES-256-GCM 加密凭据，不存储在磁盘上。
    """
    return hash_secret_raw(
        secret=password.encode(),
        salt=ARGON2_SALT,
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEM_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=ARGON2_KEY_LENGTH,
        type=Type.ID,
    )


def create_access_token(session_id: str) -> str:
    """签发 JWT.

    JWT 仅携带 session_id，不携带密钥。
    解密密钥存储在 app.state.decrypt_key 中。
    """
    from jose import jwt as jose_jwt

    settings = get_settings()
    secret = settings.secret_key.encode() if settings.secret_key else _get_or_create_secret_key()

    expire = datetime.now(UTC) + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        "sub": session_id,
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jose_jwt.encode(payload, secret, algorithm="HS256")


def verify_access_token(token: str) -> dict:
    """验证 JWT，返回 payload."""
    from jose import jwt as jose_jwt
    from jose.exceptions import JWTError

    settings = get_settings()
    secret = settings.secret_key.encode() if settings.secret_key else _get_or_create_secret_key()

    try:
        return jose_jwt.decode(token, secret, algorithms=["HS256"])
    except JWTError:
        raise


def generate_session_id() -> str:
    return uuid.uuid4().hex


def _get_or_create_secret_key() -> bytes:
    """获取或生成 JWT 签名密钥."""
    settings = get_settings()
    if not settings.secret_key:
        import secrets
        new_key = secrets.token_hex(32)
        settings.secret_key = new_key
    return settings.secret_key.encode()
