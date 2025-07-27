# HistoriCulture

HistoriCulture は、Google 検索の結果を自動でクロールし、Gemini による埋め込みと ChromaDB への格納を行う簡易 RAG (Retrieval Augmented Generation) サンプルです。収集したデータをもとに、質問に対して AI が回答を生成します。多言語（英語/日本語）対応。

## ディレクトリ構成

- `api/` - FastAPI で実装された API。`main.py` からアプリを起動します。
- `rag/` - テキストの分割 (`chunk.py`)、埋め込み (`embed.py`)、ベクターデータベース操作 (`vectordb.py`)、回答生成 (`generate.py`) をまとめたモジュール群。
- `scripts/` - 検索 (`search.py`) や Web クロール (`crawl.py`) の補助スクリプト。
- `templates/` - Web インターフェース用の HTML テンプレート。
- `tests/` - pytest 用の簡単なテストコード。
- `translations/` - 多言語翻訳ファイル。
- `Dockerfile` - 本アプリを実行するための Docker 設定。
- `requirements.txt` - 必要な Python パッケージ一覧。

## 使い方

1. 依存ライブラリをインストールします。

```bash
pip install -r requirements.txt
