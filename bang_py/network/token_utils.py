"""Utilities for generating and parsing encrypted join tokens."""

from __future__ import annotations

import json
import os
from cryptography.fernet import Fernet

# Default key for join tokens used in tests and examples.
DEFAULT_TOKEN_KEY = b"xPv7Sx0hWCLo5A9HhF_zvg87gdRSB8OYBjWM7lV-H2I="

ENV_TOKEN_KEY = "BANG_TOKEN_KEY"

__all__ = ["generate_join_token", "parse_join_token", "DEFAULT_TOKEN_KEY"]


def _token_key_bytes(key: bytes | str | None) -> bytes:
    """Return ``key`` as bytes or read it from ``BANG_TOKEN_KEY``.

    Raises:
        ValueError: If no key is provided and the environment variable is unset.
    """

    if key is None:
        env = os.getenv(ENV_TOKEN_KEY)
        if env is None:
            raise ValueError(
                "Token key not provided and BANG_TOKEN_KEY environment variable is missing"
            )
        key = env
    return key if isinstance(key, bytes) else key.encode()


def generate_join_token(host: str, port: int, code: str, key: bytes | str | None = None) -> str:
    """Return an encrypted token identifying a game room."""

    key_bytes = _token_key_bytes(key)
    data = json.dumps({"host": host, "port": port, "code": code}).encode()
    return Fernet(key_bytes).encrypt(data).decode()


def parse_join_token(token: str, key: bytes | str | None = None) -> tuple[str, int, str]:
    """Decode ``token`` and return ``(host, port, code)``."""

    key_bytes = _token_key_bytes(key)
    data = Fernet(key_bytes).decrypt(token.encode())
    obj = json.loads(data.decode())
    return obj["host"], int(obj["port"]), obj["code"]
