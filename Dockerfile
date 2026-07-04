FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV HOST="0.0.0.0"
# Cloud Run sets PORT environment variable automatically
ENV PORT="8080" 

CMD ["sh", "-c", "uvicorn src.main:app --host $HOST --port $PORT"]
