"""Password reuse detection helpers."""

from __future__ import annotations

import logging
from collections import Counter
from difflib import SequenceMatcher
from typing import TypedDict

log = logging.getLogger(__name__)


class ReuseResult(TypedDict):
    """Structured result for reuse detection."""

    exact: dict[str, int]
    similar: list[tuple[str, str, float]]


def detect_reuse(
    passwords: list[str],
    similarity_threshold: float = 0.85,
    max_similarity_pairs: int = 5000,
) -> ReuseResult:
    """Find exact and near-duplicate passwords in a list."""
    if not 0.0 <= similarity_threshold <= 1.0:
        raise ValueError("similarity_threshold must be between 0.0 and 1.0")
    if max_similarity_pairs < 0:
        raise ValueError("max_similarity_pairs must be non-negative")

    counts = Counter(p for p in passwords if p)
    exact = {password: count for password, count in counts.items() if count > 1}
    uniq = list(counts.keys())
    n = len(uniq)

    similar: list[tuple[str, str, float]] = []
    pair_budget = max_similarity_pairs
    if n > 1 and pair_budget > 0:
        # Limit O(n^2) similarity checks; exact duplicate counting is already O(n).
        for i in range(n):
            if pair_budget <= 0:
                break
            for j in range(i + 1, n):
                if pair_budget <= 0:
                    break
                a, b = uniq[i], uniq[j]
                s = SequenceMatcher(None, a, b).ratio()
                if s >= similarity_threshold:
                    similar.append((a, b, s))
                pair_budget -= 1
    log.info("reuse_detect: inputs=%d uniq=%d exact=%d similar=%d", len(passwords), n, len(exact), len(similar))
    return {"exact": exact, "similar": similar}

