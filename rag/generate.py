# rag/generate.py

from __future__ import annotations

import os
from typing import AsyncGenerator

import google.generativeai as genai

from .vectordb import VectorDB

# Configure Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Use the flash model
MODEL = genai.GenerativeModel("gemini-2.5-flash")

# System prompt without {context} placeholder—
# 本文中で f-string で組み立てます
SYS_PROMPT = (
    "You are a helpful and knowledgeable historian.\n"
    "Based only on the provided context, answer the user's question clearly and concisely.\n"
    "If the context does not contain the answer, state that you cannot answer from the given information."
)

async def answer(question: str, db: VectorDB, n_results: int = 5) -> AsyncGenerator[str, None]:
    """
    RAG: 1) テキスト質問を内部で埋め込み→検索  2) コンテキスト作成
         3) LLMへのプロンプトを組み立て  4) ストリーミング応答
    """
    # 1) 質問文字列からベクトル検索
    matches = db.query(question, n_results=n_results)

    # ヒットなしは丁寧に応答
    if not matches:
        yield "申し訳ありませんが、関連する情報がデータベースに見つかりませんでした。"
        return

    # 2) コンテキスト結合
    context = "\n\n".join(match["document"] for match in matches)

    # 3) プロンプト組み立て （必ず context を挟む）
    prompt = (
        f"{SYS_PROMPT}\n\n"
        f"Context:\n{context}\n\n"
        f"User Question: {question}\n"
        "Answer:"
    )

    # 4) Gemini にストリーミングで投げる
    try:
        response_stream = await MODEL.generate_content_async(prompt, stream=True)
        async for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"申し訳ありません、回答生成中にエラーが発生しました: {e}"

