FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Qdrant Cloud переменные
ENV QDRANT_URL=https://6147f21b-c372-4319-9945-285e453a502d.eu-west-1-0.aws.cloud.qdrant.io
ENV QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6MDdkMTU0ODktYzdjMy00YmE1LTg0YzUtZDU1YTYzMGU4MDk5In0.x6PUPEQqpap0OQM460jZP5_ZGieI9-jfUEeTV3_v9PY

WORKDIR /app

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/

WORKDIR /app/backend

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]