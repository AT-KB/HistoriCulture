#!/usr/bin/env sh
set -e
if [ "$RUN_MODE" = "worker" ]; then
  echo "[entrypoint] Running ingestion worker..."
  exec python api/worker.py
else
  echo "[entrypoint] Starting FastAPI server on port $PORT..."
  exec uvicorn api.main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 60
fi
