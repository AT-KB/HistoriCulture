#!/usr/bin/env sh
set -e
# RUN_MODE: "web" (default) or "worker"
if [ "$RUN_MODE" = "worker" ]; then
  echo "[entrypoint] Running ingestion worker..."
  exec python api/worker.py
else
  echo "[entrypoint] Starting FastAPI server..."
  exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --timeout-keep-alive 60  # 8000 → ${PORT:-8000}
fi
