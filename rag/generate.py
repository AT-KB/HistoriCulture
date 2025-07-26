from __future__ import annotations

import os
from typing import AsyncGenerator

import google.generativeai as genai

from .vectordb import VectorDB
from .embed import GeminiEmbedding

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = genai.GenerativeModel("gemini-2.5-flash")

SYS_PROMPT = """
You are a helpful and knowledgeable historian.
Based *only* on the provided context, answer the user's question clearly and concisely.
If the context does not contain the answer, state that you cannot answer from the given information.
"""

async def answer(question: str, db: VectorDB, n_results: int = 5) -> AsyncGenerator[str, None]:
    # 1) 質問文字列からマッチングチャンクを取得
    matches = db.query(question, n_results=n_results)

    if not matches:
        yield "申し訳ありませんが、関連する情報がデータベースに見つかりませんでした。"
        return

    # 2) コンテキスト生成
    context = "\n\n".join(match["document"] for match in matches)
    prompt = SYS_PROMPT.replace("{context}", context) + f"\nUser Question: {question}"

    # 3) モデル呼び出し（ストリーミング）
    try:
        response_stream = await MODEL.generate_content_async(prompt, stream=True)
        async for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        error_message = f"申し訳ありません、回答生成中にエラーが発生しました: {e}"
        yield error_message
