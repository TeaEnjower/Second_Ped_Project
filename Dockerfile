FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем pyproject.toml
COPY pyproject.toml .

# Устанавливаем только зависимости из pyproject.toml, без установки проекта
RUN pip install --no-cache-dir pip-tools && \
    pip-compile --generate-hashes -o requirements.txt pyproject.toml && \
    pip install --no-cache-dir -r requirements.txt

# Теперь копируем исходный код
COPY . .

# Проверяем что зависимости установлены
RUN python -c "import celery; print(f'✓ Celery {celery.__version__} installed')"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]