from __future__ import annotations

import os
from typing import Generator

import google.generativeai as genai

from .vectordb import VectorDB


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = genai.GenerativeModel("gemini-pro")


def answer(question: str, db: VectorDB, n_results: int = 5) -> Generator[str, None, None]:
    """Generate answer using retrieved documents and Gemini Pro."""
    matches = db.query(question, n_results)
    context = "\n".join(match["document"] for match in matches)
    prompt = f"{context}\n\nQ: {question}\nA:"
    for chunk in MODEL.generate_content(prompt, stream=True):
        yield chunk.text  # type: ignore[attr-defined]
