# Используем официальный легковесный образ Python 3.13
FROM python:3.13-slim

# Устанавливаем системные зависимости для работы базы данных и сборки пакетов
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем Poetry напрямую через pip
RUN pip install --no-cache-dir poetry gunicorn

# Отключаем создание виртуальных окружений внутри контейнера, ставим пакеты прямо в систему
RUN poetry config virtualenvs.create false

# Копируем файлы зависимостей проекта
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости без режима сборки самого пакета
RUN poetry install --no-root

# Копируем весь остальной код проекта в контейнер
COPY . .

# Открываем порт для внутренней связи с Nginx
EXPOSE 8000
