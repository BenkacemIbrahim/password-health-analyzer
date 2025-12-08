from typing import List, Dict, Tuple
from difflib import SequenceMatcher
import logging

log = logging.getLogger(__name__)


def detect_reuse(passwords: List[str], similarity_threshold: float = 0.85, max_similarity_pairs: int = 5000) -> Dict[str, object]:
    counts: Dict[str, int] = {}
    for p in passwords:
        if p:
            counts[p] = counts.get(p, 0) + 1
    exact = {p: c for p, c in counts.items() if c > 1}
    uniq = list(counts.keys())
    n = len(uniq)

    similar: List[Tuple[str, str, float]] = []
    pair_budget = max_similarity_pairs
    if n > 1 and pair_budget > 0:
        # Limit O(n^2) similarity checks using a simple budget; exact duplicates already O(n)
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

