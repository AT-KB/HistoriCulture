# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway provides the PORT env var.
EXPOSE ${PORT:-8000}

#CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
# --- ★★★★★ ここが最後の修正点 ★★★★★ ---
# python -u で非バッファモードで実行し、print文がリアルタイムでログに出るようにする
CMD ["python", "-u", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
