#!/usr/bin/env sh
set -e
# RUN_MODE: "web" (default) or "worker"
if [ "$RUN_MODE" = "worker" ]; then
  echo "[entrypoint] Running ingestion worker..."
  exec python api/worker.py
else
  echo "[entrypoint] Starting FastAPI server..."
  exec uvicorn api.main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 60  # PORT必須、デフォルト削除
fi
