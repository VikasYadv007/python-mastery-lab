"""Username and password primitives without database or UI dependencies."""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets

USERNAME_RE = re.compile(r"[a-z][a-z0-9_.-]{2,29}\Z")


def normalize_username(value: str) -> str:
    result = value.strip().lower()
    if not USERNAME_RE.fullmatch(result):
        raise ValueError(
            "Username must be 3–30 characters: lowercase letters, numbers, _, . or -, starting with a letter."
        )
    return result


def make_password_hash(password: str) -> str:
    if len(password) < 10 or len(password) > 200:
        raise ValueError("Password must be 10–200 characters.")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return (
        "scrypt$16384$8$1$"
        + base64.b64encode(salt).decode()
        + "$"
        + base64.b64encode(digest).decode()
    )


def verify_password(password: str, encoded: str) -> bool:
    if (
        not isinstance(password, str)
        or not 10 <= len(password) <= 200
        or not isinstance(encoded, str)
    ):
        return False
    try:
        algo, n, r, p, salt, expected = encoded.split("$")
        if algo != "scrypt" or (int(n), int(r), int(p)) != (16384, 8, 1):
            return False
        decoded_salt = base64.b64decode(salt, validate=True)
        decoded_expected = base64.b64decode(expected, validate=True)
        if len(decoded_salt) != 16 or len(decoded_expected) != 64:
            return False
        digest = hashlib.scrypt(
            password.encode("utf-8"), salt=decoded_salt, n=int(n), r=int(r), p=int(p)
        )
        return hmac.compare_digest(digest, decoded_expected)
    except (ValueError, TypeError, UnicodeError):
        return False
