"""
Small deterministic embedding for local legal snippets.

This avoids downloading external models when importing public Chongqing sources.
It is not a semantic embedding replacement, but it gives Chroma a stable vector
space for lightweight local retrieval.
"""

from __future__ import annotations

import hashlib
import math
from typing import Iterable, List


DIMENSION = 512


def embed_text(text: str, dimension: int = DIMENSION) -> List[float]:
    vector = [0.0] * dimension
    tokens = _tokenize(text)
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [round(value / norm, 6) for value in vector]


def embed_texts(texts: Iterable[str], dimension: int = DIMENSION) -> List[List[float]]:
    return [embed_text(text, dimension) for text in texts]


def _tokenize(text: str) -> List[str]:
    normalized = "".join(ch if ch.isalnum() else " " for ch in text.lower())
    words = [word for word in normalized.split() if word]
    chars = [normalized[i : i + 2] for i in range(max(0, len(normalized) - 1))]
    return words + chars
