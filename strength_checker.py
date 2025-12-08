import re
import math
import logging
from typing import Iterable, Dict, Any

log = logging.getLogger(__name__)


_COMMON_PASSWORDS = {
    "123456","password","12345678","qwerty","123456789","12345","1234","111111","1234567","dragon",
    "baseball","iloveyou","trustno1","123123","sunshine","master","welcome","shadow","ashley","football",
    "jesus","michael","ninja","mustang","password1","password123","admin","login","princess","qwerty123",
    "abc123","monkey","letmein","solo","qazwsx","zaq1zaq","1q2w3e4r","passw0rd","hello","freedom","whatever",
    "qwertyuiop","asdfghjkl","zxcvbnm","superman","hottie","loveme","flower","696969","batman","654321",
    "super","passwort","password!","lovely","aaa111","123qwe","1qaz2wsx","121212","qwe123","q1w2e3r4",
    "qwerty1","qwerty!","qwert","qwert!","pass","pass123","welcome1","welcome123","abcd1234","qweasd",
    "pepper","harley","ranger","charlie","daniel","hunter","buster","taylor","andrew","thomas","joshua",
    "soccer","starwars","jennifer","love","orange","computer","michelle","123abc","1q2w3e","q1w2e3",
}

_KEYBOARD_ROWS = [
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
    "1234567890",
]


def _contains_any(s: str, patterns: Iterable[str]) -> bool:
    low = s.lower()
    return any(p in low for p in patterns)


def _has_keyboard_sequence(s: str) -> bool:
    low = s.lower()
    for row in _KEYBOARD_ROWS:
        if _has_sequence_in(low, row) or _has_sequence_in(low, row[::-1]):
            return True
    return False


def _has_sequence_in(s: str, seq: str, k: int = 4) -> bool:
    for i in range(len(seq) - k + 1):
        sub = seq[i : i + k]
        if sub in s:
            return True
    return False


def _has_monotonic_sequence(s: str, k: int = 4) -> bool:
    if len(s) < k:
        return False
    for i in range(len(s) - k + 1):
        chunk = s[i : i + k]
        if all(ord(chunk[j + 1]) - ord(chunk[j]) == 1 for j in range(k - 1)):
            return True
        if all(ord(chunk[j]) - ord(chunk[j + 1]) == 1 for j in range(k - 1)):
            return True
    return False


def analyze_password(pwd: str) -> Dict[str, Any]:
    if not pwd:
        return {"score": 0, "entropy_bits": 0.0, "length": 0, "lower": False, "upper": False, "digit": False, "symbol": False, "common": False, "sequence": False, "keyboard": False, "repeats": False}

    length = len(pwd)
    lower = any(c.islower() for c in pwd)
    upper = any(c.isupper() for c in pwd)
    digit = any(c.isdigit() for c in pwd)
    symbol = any(not c.isalnum() for c in pwd)

    charset = 0
    if lower:
        charset += 26
    if upper:
        charset += 26
    if digit:
        charset += 10
    if symbol:
        charset += 32
    entropy_bits = length * math.log2(charset) if charset > 0 else 0.0

    common = pwd.lower() in _COMMON_PASSWORDS
    repeats = bool(re.search(r"(.)\1{2,}", pwd))
    sequence = _has_monotonic_sequence(pwd.lower(), 4)
    keyboard = _has_keyboard_sequence(pwd)

    score = 0
    if length >= 16:
        score += 3
    elif length >= 12:
        score += 2
    elif length >= 8:
        score += 1

    cats = sum([1 if lower else 0, 1 if upper else 0, 1 if digit else 0, 1 if symbol else 0])
    if cats >= 4:
        score += 3
    elif cats == 3:
        score += 2
    elif cats == 2:
        score += 1

    if entropy_bits >= 60:
        score += 4
    elif entropy_bits >= 40:
        score += 3
    elif entropy_bits >= 28:
        score += 2
    elif entropy_bits >= 18:
        score += 1

    if common:
        score -= 5
    if sequence or keyboard:
        score -= 2
    if repeats:
        score -= 1

    score = max(0, min(10, score))
    result = {
        "score": score,
        "entropy_bits": round(entropy_bits, 2),
        "length": length,
        "lower": lower,
        "upper": upper,
        "digit": digit,
        "symbol": symbol,
        "common": common,
        "sequence": sequence,
        "keyboard": keyboard,
        "repeats": repeats,
        "categories": cats,
    }
    log.info("analyze: len=%d cats=%d entropy=%.2f score=%d", length, cats, result["entropy_bits"], score)
    return result


def score_password(pwd: str) -> int:
    return analyze_password(pwd)["score"]
