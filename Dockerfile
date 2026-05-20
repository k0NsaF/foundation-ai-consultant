FROM python:3.11-slim

# Создаём непривилегированного пользователя (как требует HF)
RUN useradd -m -u 1000 user
USER user

WORKDIR /app

# HF кэш будет в доступной для записи директории
ENV HF_HOME=/app/hf_cache

# Копируем зависимости
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Копируем код с правильными правами
COPY --chown=user backend/ ./backend/

WORKDIR /app/backend

# HF Spaces ожидает порт 7860
EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]