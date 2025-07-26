# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Add entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
# Default to web mode
ENV RUN_MODE=web

# Railway provides the PORT env var.
EXPOSE ${PORT:-8000}

#CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
# python -u で非バッファモードで実行し、print文がリアルタイムでログに出るようにする
CMD ["python", "-u", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
