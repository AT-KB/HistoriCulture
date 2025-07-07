# rag/generate.py
from __future__ import annotations

import os
from typing import AsyncGenerator

import google.generativeai as genai

from .vectordb import VectorDB
from .embed import GeminiEmbedding  # このimportが今度こそ成功します

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 司令塔の指示通り、最新モデルを使用
MODEL = genai.GenerativeModel("gemini-2.5-flash")

SYS_PROMPT = """
You are a helpful and knowledgeable historian.
Based *only* on the provided context, answer the user's question clearly and concisely.
If the context does not contain the answer, state that you cannot answer from the given information.
"""

async def answer(question: str, db: VectorDB, n_results: int = 5) -> AsyncGenerator[str, None]:
    """
    Generates a streaming answer.
    """
    # 1. Create an instance of our embedding class
    embedder = GeminiEmbedding()
    # 2. Use it to create a vector from the user's question
    question_embedding = embedder.embed_query(text=question)
    # 3. Query the DB with the generated vector
    matches = db.query(query_embedding=question_embedding, n_results=n_results)

    if not matches:
        yield "申し訳ありませんが、関連する情報がデータベースに見つかりませんでした。"
        return

    context = "\n\n".join(match["document"] for match in matches)
    prompt = SYS_PROMPT.format(context=context) + f"\nUser Question: {question}"

    try:
        response_stream = await MODEL.generate_content_async(prompt, stream=True)
        async for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        error_message = f"申し訳ありません、回答の生成中にエラーが発生しました: {e}"
        print(error_message)
        yield error_message
