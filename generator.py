import secrets
import string
import random


def generate_password(
    length: int = 16,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
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
    random.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)

