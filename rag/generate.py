# rag/generate.py
from __future__ import annotations

import os
from typing import AsyncGenerator

import google.generativeai as genai

from .vectordb import VectorDB

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- ★★★★★ 司令塔の最新情報に基づき修正 ★★★★★ ---
# 司令塔の指示に基づき、モデル名を最新の 'gemini-2.5-flash' に設定します。
MODEL = genai.GenerativeModel("gemini-2.5-flash")
# ---

# プロンプトも少し調整して、役割を明確にします。
SYS_PROMPT = """
You are a helpful and knowledgeable historian.
Based *only* on the provided context, answer the user's question clearly and concisely.
If the context does not contain the answer, state that you cannot answer from the given information.

Provided Context:
---
{context}
---
"""

# 以前の非同期ストリーミング対応の'answer'関数に戻します。
async def answer(question: str, db: VectorDB, n_results: int = 5) -> AsyncGenerator[str, None]:
    """
    Generate a streaming answer using retrieved documents and Gemini Pro asynchronously.
    """
    matches = db.query(question, n_results)
    if not matches:
        yield "申し訳ありませんが、関連する情報がデータベースに見つかりませんでした。"
        return

    context = "\n\n".join(match["document"] for match in matches)
    prompt = SYS_PROMPT.format(context=context) + f"\nUser Question: {question}"

    try:
        # 非同期でストリーミング生成を呼び出します
        response_stream = await MODEL.generate_content_async(prompt, stream=True)
        async for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        error_message = f"申し訳ありません、回答の生成中にエラーが発生しました: {e}"
        print(error_message)
        yield error_message
