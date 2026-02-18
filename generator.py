"""Secure password generation utilities."""

from __future__ import annotations

import secrets
import string


def generate_password(
    length: int = 16,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    """Generate a cryptographically secure password.

    Ensures every enabled character category appears at least once.
    """
    if length <= 0:
        raise ValueError("Length must be greater than zero")

    categories = []
    if use_upper:
        categories.append(string.ascii_uppercase)
    if use_lower:
        categories.append(string.ascii_lowercase)
    if use_digits:
        categories.append(string.digits)
    if use_symbols:
        categories.append("!@#$%^&*()-_=+[]{};:,./?""'`~|\\")
    if not categories:
        raise ValueError("At least one character category must be enabled")
    if length < len(categories):
        raise ValueError("Length must be at least the number of enabled categories")

    pool = "".join(categories)
    password_chars = [secrets.choice(cat) for cat in categories]
    remaining = length - len(password_chars)
    for _ in range(remaining):
        password_chars.append(secrets.choice(pool))
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)

