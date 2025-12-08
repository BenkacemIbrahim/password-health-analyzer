import json
import base64
import hashlib
import hmac
import secrets
from typing import List

try:
    from cryptography.fernet import Fernet  # type: ignore
    _HAS_CRYPTO = True
except Exception:
    _HAS_CRYPTO = False


def _b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("ascii")


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s.encode("ascii"))


def _derive_key(password: str, salt: bytes, dklen: int = 32) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000, dklen=dklen)


def save_passwords(path: str, passwords: List[str], master_password: str) -> None:
    data = "\n".join(passwords).encode("utf-8")
    salt = secrets.token_bytes(16)
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
        tag = hmac.new(mac_key, ct, "sha256").digest()
        blob = {
            "v": 1,
            "method": "pbkdf2_xor",
            "salt": _b64e(salt),
            "iv": _b64e(iv),
            "ct": _b64e(ct),
            "tag": _b64e(tag),
        }
    with open(path, "w", encoding="utf-8") as fobj:
        json.dump(blob, fobj)


def load_passwords(path: str, master_password: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as fobj:
        blob = json.load(fobj)
    method = blob.get("method")
    salt = _b64d(blob["salt"])  # type: ignore
    if method == "fernet" and _HAS_CRYPTO:
        key = _derive_key(master_password, salt, 32)
        fkey = base64.urlsafe_b64encode(key)
        f = Fernet(fkey)
        ct = _b64d(blob["ct"])  # type: ignore
        pt = f.decrypt(ct)
    elif method == "pbkdf2_xor":
        enc_key = _derive_key(master_password, salt, 32)
        mac_key = _derive_key(master_password, salt + b"mac", 32)
        iv = _b64d(blob["iv"])  # type: ignore
        ct = _b64d(blob["ct"])  # type: ignore
        tag = _b64d(blob["tag"])  # type: ignore
        calc_tag = hmac.new(mac_key, ct, "sha256").digest()
        if not hmac.compare_digest(tag, calc_tag):
            raise ValueError("Integrity check failed: wrong password or corrupted file")
        pt = _xor_stream_decrypt(ct, enc_key, iv)
    else:
        raise ValueError("Unsupported storage method or missing cryptography library")
    text = pt.decode("utf-8")
    return [line for line in text.splitlines() if line]


def _xor_stream_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    return _xor_stream(data, key, iv)


def _xor_stream_decrypt(ct: bytes, key: bytes, iv: bytes) -> bytes:
    return _xor_stream(ct, key, iv)


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

