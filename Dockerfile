FROM python:3.11-slim

# Hugging Face Spaces требует непривилегированного пользователя
RUN useradd -m -u 1000 user
USER user

WORKDIR /app

# Кэш для моделей sentence-transformers
ENV HF_HOME=/app/hf_cache

# Копируем зависимости
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Копируем код
COPY backend/ ./backend/

WORKDIR /app/backend

# HF Spaces требует порт 7860
EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]