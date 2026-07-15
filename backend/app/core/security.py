"""Security primitives: JWT, password hashing, Telegram initData validation.

No DB access here — pure crypto/token helpers so they stay trivially testable.
"""
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import parse_qsl

import bcrypt
import jwt

from app.core.config import settings

# bcrypt operates on the first 72 bytes; truncate explicitly so long inputs
# hash deterministically instead of raising.
_BCRYPT_MAX = 72


# --- Passwords -------------------------------------------------------------

def hash_password(raw: str) -> str:
    digest = bcrypt.hashpw(raw.encode("utf-8")[:_BCRYPT_MAX], bcrypt.gensalt())
    return digest.decode("utf-8")


def verify_password(raw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(raw.encode("utf-8")[:_BCRYPT_MAX], hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# --- JWT -------------------------------------------------------------------

def create_access_token(subject: str | int, extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Raises jwt.PyJWTError on invalid/expired tokens."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


# --- Telegram WebApp initData validation -----------------------------------
# https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app

def validate_telegram_init_data(init_data: str, bot_token: str | None = None) -> dict[str, Any] | None:
    """Verify Telegram Mini App initData HMAC. Returns parsed user dict or None."""
    token = bot_token or settings.telegram_bot_token
    if not token or not init_data:
        return None

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{k}={parsed[k]}" for k in sorted(parsed))
    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    user_raw = parsed.get("user")
    if not user_raw:
        return None
    try:
        return json.loads(user_raw)
    except json.JSONDecodeError:
        return None
