from __future__ import annotations

from typing import List

try:
    import tiktoken
except ImportError:  # pragma: no cover - optional dependency
    tiktoken = None


def _encode(text: str) -> List[int]:
    if tiktoken:
        enc = tiktoken.get_encoding("cl100k_base")
        return enc.encode(text)
    return text.split()


def _decode(tokens: List[int]) -> str:
    if tiktoken:
        enc = tiktoken.get_encoding("cl100k_base")
        return enc.decode(tokens)
    return " ".join(tokens)


def chunk_text(text: str, max_tokens: int = 200) -> List[str]:
    """Split text into token chunks."""
    tokens = _encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i : i + max_tokens]
        chunks.append(_decode(chunk_tokens))
    return chunks
