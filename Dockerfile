# Dockerfile
# Базовый образ для Python
FROM python:3.11-slim

# Устанавливаем зависимости для PostgreSQL и других пакетов
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc python3-dev musl-dev netcat-openbsd curl && apt-get clean && rm -rf /var/lib/apt/lists/*


# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Экспортируем порт
EXPOSE 8000

# Запускаем команду, которая будет выполняться при запуске контейнера
CMD ["sh", "-c", "until nc -z $DB_HOST $DB_PORT; do echo 'Waiting for the database...'; sleep 2; done && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
