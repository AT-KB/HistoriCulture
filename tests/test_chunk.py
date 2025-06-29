import pytest
from rag.chunk import chunk_text


def test_chunk_text_split():
    text = "one two three four five"
    chunks = chunk_text(text, max_tokens=2)
    assert chunks == ["one two", "three four", "five"]
