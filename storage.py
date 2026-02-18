"""Encrypted persistence helpers for password lists.

Preferred encryption uses `cryptography.fernet`. A deterministic fallback based on
PBKDF2 + HMAC + XOR stream exists for environments where `cryptography` is
unavailable, but Fernet should always be preferred for stronger guarantees.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from pathlib import Path
from typing import Any

try:
    from cryptography.fernet import Fernet  # type: ignore
    _HAS_CRYPTO = True
except Exception:
    _HAS_CRYPTO = False


PBKDF2_ROUNDS = 200_000
SALT_LENGTH = 16


def _b64e(data: bytes) -> str:
    """Encode bytes as URL-safe base64 text."""
    return base64.urlsafe_b64encode(data).decode("ascii")


def _b64d(text: str) -> bytes:
    """Decode URL-safe base64 text to bytes."""
    return base64.urlsafe_b64decode(text.encode("ascii"))


def _derive_key(password: str, salt: bytes, dklen: int = 32) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS, dklen=dklen)


def _compute_tag(mac_key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    """Authenticate IV and ciphertext to prevent tampering."""
    return hmac.new(mac_key, iv + ciphertext, "sha256").digest()


def save_passwords(path: str | Path, passwords: list[str], master_password: str) -> None:
    """Encrypt and save a list of passwords to disk."""
    file_path = Path(path)
    data = "\n".join(passwords).encode("utf-8")
    salt = secrets.token_bytes(SALT_LENGTH)

    blob: dict[str, Any]
    if _HAS_CRYPTO:
        key = _derive_key(master_password, salt, 32)
        fkey = base64.urlsafe_b64encode(key)
        f = Fernet(fkey)
        ct = f.encrypt(data)
        blob = {"v": 1, "method": "fernet", "salt": _b64e(salt), "ct": _b64e(ct)}
    else:
        enc_key = _derive_key(master_password, salt, 32)
        mac_key = _derive_key(master_password, salt + b"mac", 32)
        iv = secrets.token_bytes(16)
        ct = _xor_stream_encrypt(data, enc_key, iv)
        tag = _compute_tag(mac_key, iv, ct)
        blob = {
            "v": 1,
            "method": "pbkdf2_xor",
            "salt": _b64e(salt),
            "iv": _b64e(iv),
            "ct": _b64e(ct),
            "tag": _b64e(tag),
        }

    file_path.write_text(json.dumps(blob, ensure_ascii=True), encoding="utf-8")


def load_passwords(path: str | Path, master_password: str) -> list[str]:
    """Load and decrypt a password list from disk."""
    file_path = Path(path)
    blob = json.loads(file_path.read_text(encoding="utf-8"))

    method = blob.get("method")
    salt = _b64d(blob["salt"])  # type: ignore[index]
    if method == "fernet" and _HAS_CRYPTO:
        key = _derive_key(master_password, salt, 32)
        fkey = base64.urlsafe_b64encode(key)
        f = Fernet(fkey)
        ct = _b64d(blob["ct"])  # type: ignore[index]
        pt = f.decrypt(ct)
    elif method == "pbkdf2_xor":
        enc_key = _derive_key(master_password, salt, 32)
        mac_key = _derive_key(master_password, salt + b"mac", 32)
        iv = _b64d(blob["iv"])  # type: ignore[index]
        ct = _b64d(blob["ct"])  # type: ignore[index]
        tag = _b64d(blob["tag"])  # type: ignore[index]
        calc_tag = _compute_tag(mac_key, iv, ct)
        if not hmac.compare_digest(tag, calc_tag):
            # Backward compatibility with older files that authenticated only ct.
            legacy_tag = hmac.new(mac_key, ct, "sha256").digest()
            if not hmac.compare_digest(tag, legacy_tag):
                raise ValueError("Integrity check failed: wrong password or corrupted file")
        pt = _xor_stream_decrypt(ct, enc_key, iv)
    else:
        raise ValueError("Unsupported storage method or missing cryptography library")

    text = pt.decode("utf-8")
    return [line for line in text.splitlines() if line]


def _xor_stream_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    return _xor_stream(data, key, iv)


def _xor_stream_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    return _xor_stream(ciphertext, key, iv)


def _xor_stream(inp: bytes, key: bytes, iv: bytes) -> bytes:
    out = bytearray()
    counter = 0
    offset = 0
    while offset < len(inp):
        block = hmac.new(key, iv + counter.to_bytes(4, "big"), "sha256").digest()
        take = min(32, len(inp) - offset)
        out.extend(b ^ block[i] for i, b in enumerate(inp[offset : offset + take]))
        offset += take
        counter += 1
    return bytes(out)

