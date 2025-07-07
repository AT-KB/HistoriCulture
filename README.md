# HistoriCulture

HistoriCulture は、Google 検索の結果を自動でクロールし、Gemini による埋め込みと ChromaDB への格納を行う簡易 RAG (Retrieval Augmented Generation) サンプルです。収集したデータをもとに、質問に対して AI が回答を生成します。

## ディレクトリ構成

- `api/` - FastAPI で実装された API。`main.py` からアプリを起動します。
- `rag/` - テキストの分割 (`chunk.py`)、埋め込み (`embed.py`)、ベクターデータベース操作 (`vectordb.py`)、回答生成 (`generate.py`) をまとめたモジュール群。
- `scripts/` - 検索 (`search.py`) や Web クロール (`crawl.py`) の補助スクリプト。
- `templates/` - Web インターフェース用の HTML テンプレート。
- `tests/` - pytest 用の簡単なテストコード。
- `Dockerfile` - 本アプリを実行するための Docker 設定。
- `requirements.txt` - 必要な Python パッケージ一覧。

## 使い方

1. 依存ライブラリをインストールします。

```bash
pip install -r requirements.txt
```

2. 環境変数を設定します。  
   - `GOOGLE_API_KEY` : Google Gemini の API キー  
   - `CSE_KEY` と `CSE_CX` : Google Custom Search の認証情報

3. API を起動します。

```bash
uvicorn api.main:app --reload
```

ブラウザで `http://localhost:8000/` にアクセスすると、質問入力フォームが表示されます。

## データの取り込み

`/ingest` エンドポイントに対してクエリを POST すると、指定のキーワードで検索した Web ページをクロールし、埋め込み後に ChromaDB に保存します。保存したデータは `/ask` エンドポイントでの回答生成に利用されます。`api/worker.py` を直接実行すると、あらかじめ用意されたトピックを順番に取り込みます。
