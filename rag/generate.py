# rag/generate.py
from __future__ import annotations

import os
from typing import AsyncGenerator

import google.generativeai as genai

from .vectordb import VectorDB
from .embed import GeminiEmbedding  # ★ 新しくインポート

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = genai.GenerativeModel("gemini-2.5-flash-latest") # 安定版の最新モデル名

SYS_PROMPT = "..." # (プロンプトは変更なし)

async def answer(question: str, db: VectorDB, n_results: int = 5) -> AsyncGenerator[str, None]:
    """
    Generates a streaming answer.
    The key change is to manually create the query embedding first.
    """
    # 1. ★★★★★ ここが最重要の修正点 ★★★★★
    # GeminiのEmbedderを呼び出し、質問文をベクトル化する
    embedder = GeminiEmbedding()
    question_embedding = embedder.embed_query(text=question)

    # 2. 作成したベクトルを使ってデータベースを検索する
    matches = db.query(query_embedding=question_embedding, n_results=n_results)
    # ---

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
