# Этап 1: "Строитель" (Builder)
# На этом этапе мы устанавливаем все зависимости, включая тяжелые сборочные инструменты.
FROM python:3.11-slim as builder

# Устанавливаем системные зависимости для сборки keystone-engine
# и сразу чистим кэш apt, чтобы слой был меньше
RUN apt-get update && apt-get install -y build-essential cmake && rm -rf /var/lib/apt/lists/*

# Создаем виртуальное окружение. Это стандартная лучшая практика.
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
# Добавляем venv в PATH, чтобы команды (pip, gunicorn) были доступны напрямую
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Копируем файл с зависимостями и устанавливаем их в виртуальное окружение
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---

# Этап 2: Финальный образ (Final Image)
# Это будет маленький и чистый образ только для запуска приложения.
FROM python:3.11-slim

# Создаем непривилегированного пользователя для безопасности, как и раньше
RUN addgroup --system app && adduser --system --group app

# Копируем готовое виртуальное окружение из "строителя"
COPY --from=builder /opt/venv /opt/venv

# Устанавливаем рабочую директорию и копируем код приложения
WORKDIR /app
COPY . .
# Делаем нашего пользователя владельцем всех файлов
RUN chown -R app:app /app

# Переключаемся на непривилегированного пользователя
USER app

# Добавляем venv в PATH и для финального образа
ENV PATH="/opt/venv/bin:$PATH"

# Указываем порт и команду запуска
EXPOSE 8000
# Используем exec-форму CMD для корректной обработки сигналов
# и ${PORT:-8000} для гибкости на облачных платформах
CMD ["/bin/sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8000} app:app"]
