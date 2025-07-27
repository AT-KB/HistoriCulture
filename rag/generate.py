# rag/generate.py

from __future__ import annotations
import os
import logging
from typing import AsyncGenerator
import google.generativeai as genai

from .vectordb import VectorDB

# 設定
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = genai.GenerativeModel("gemini-2.5-flash")
logger = logging.getLogger(__name__)

SYS_PROMPT = (
    "You are a helpful and knowledgeable historian.\n"
    "Based only on the provided context, answer the user's question clearly and concisely.\n"
    "If the context does not contain the answer, state that you cannot answer from the given information.\n"
    "Answer in the language of the query."  # 言語対応追加
)

async def answer(question: str, db: VectorDB, n_results: int = 5) -> AsyncGenerator[str, None]:
    logger.info(f"[ASK] question received: {question!r}")
    # 1) ベクトル検索
    matches = db.query(question, n_results=n_results)
    logger.info(f"[ASK] {len(matches)} chunks matched")

    if not matches:
        yield "申し訳ありませんが、関連する情報がデータベースに見つかりませんでした。"
        return

    # 2) コンテキスト結合
    context = "\n\n".join(m["document"] for m in matches)

    # 3) プロンプト組み立て
    prompt = (
        f"{SYS_PROMPT}\n\n"
        f"Context:\n{context}\n\n"
        f"User Question: {question}\n\n"
        "Answer:"
    )
    logger.info(f"[ASK] prompt length: {len(prompt)} chars")

    # 4) Gemini へストリーミング
    try:
        stream = await MODEL.generate_content_async(prompt, stream=True)
        async for chunk in stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        logger.exception("Generation error")
        yield f"申し訳ありません、回答生成中にエラーが発生しました: {e}"
