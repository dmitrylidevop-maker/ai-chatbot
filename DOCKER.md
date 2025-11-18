# Docker Deployment Guide

Инструкция по запуску AI Chat Bot в Docker контейнере.

## Требования

- Docker 20.10+
- 8GB+ RAM (для Ollama модели)
- PostgreSQL (может быть на хосте или в отдельном контейнере)

## Быстрый старт

### 1. Подготовка

Убедитесь, что файл `.env` настроен правильно:

```bash
# Database Configuration (должен указывать на доступную БД)
DB_HOST=192.168.31.129  # IP хоста или другого контейнера
DB_PORT=5435
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password

# Ollama Configuration
OLLAMA_MODEL=llama3:8b
OLLAMA_BASE_URL=http://localhost:11434

# Application Configuration
SECRET_KEY=your-secret-key-change-in-production
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Важно**: `DB_HOST` должен быть доступен из контейнера. Не используйте `localhost` если БД на хосте.

### 2. Сборка образа

```bash
chmod +x docker-build.sh docker-run.sh
./docker-build.sh
```

Это создаст Docker образ `ai-chatbot:latest`.

### 3. Запуск контейнера

```bash
./docker-run.sh
```

Контейнер запустится и будет доступен на `http://localhost:8000`

## Ручные команды Docker

### Сборка

```bash
docker build -t ai-chatbot:latest .
```

### Запуск

```bash
docker run -d \
  --name ai-chatbot-app \
  --env-file .env \
  -p 8000:8000 \
  --restart unless-stopped \
  ai-chatbot:latest
```

### Просмотр логов

```bash
docker logs -f ai-chatbot-app
```

### Остановка

```bash
docker stop ai-chatbot-app
```

### Удаление контейнера

```bash
docker rm ai-chatbot-app
```

### Вход в контейнер

```bash
docker exec -it ai-chatbot-app /bin/bash
```

## Работа с базой данных

### PostgreSQL на хосте

Если PostgreSQL запущен на хост-машине, используйте:

**Linux/Mac**:
```bash
DB_HOST=host.docker.internal  # или IP хоста
```

**Или используйте network mode host**:
```bash
docker run -d \
  --name ai-chatbot-app \
  --env-file .env \
  --network host \
  ai-chatbot:latest
```

### PostgreSQL в отдельном контейнере

1. Создайте Docker сеть:
```bash
docker network create chatbot-network
```

2. Запустите PostgreSQL:
```bash
docker run -d \
  --name postgres-db \
  --network chatbot-network \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=chatbot_db \
  -p 5432:5432 \
  postgres:16
```

3. Обновите `.env`:
```bash
DB_HOST=postgres-db
DB_PORT=5432
DB_NAME=chatbot_db
```

4. Запустите приложение:
```bash
docker run -d \
  --name ai-chatbot-app \
  --network chatbot-network \
  --env-file .env \
  -p 8000:8000 \
  ai-chatbot:latest
```

## Проверка работы

### Health Check

```bash
curl http://localhost:8000/health
```

### API Documentation

Откройте в браузере: `http://localhost:8000/docs`

### Тестовый запрос

```bash
# Регистрация
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Вход
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

## Обновление приложения

```bash
# Остановить и удалить старый контейнер
docker stop ai-chatbot-app
docker rm ai-chatbot-app

# Пересобрать образ
./docker-build.sh

# Запустить новый контейнер
./docker-run.sh
```

## Объем данных (опционально)

Для сохранения моделей Ollama между перезапусками:

```bash
docker run -d \
  --name ai-chatbot-app \
  --env-file .env \
  -p 8000:8000 \
  -v ollama-models:/root/.ollama \
  ai-chatbot:latest
```

## Troubleshooting

### Контейнер не запускается

```bash
# Проверьте логи
docker logs ai-chatbot-app

# Проверьте что .env существует
ls -la .env
```

### Не удается подключиться к PostgreSQL

```bash
# Проверьте что БД доступна
docker exec -it ai-chatbot-app psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME

# Проверьте сетевые настройки
docker inspect ai-chatbot-app | grep -A 20 NetworkSettings
```

### Ollama модель не загружается

```bash
# Войдите в контейнер
docker exec -it ai-chatbot-app /bin/bash

# Проверьте Ollama
ollama list

# Загрузите модель вручную
ollama pull llama3:8b
```

### Мало памяти

Ollama требует минимум 8GB RAM. Проверьте:

```bash
docker stats ai-chatbot-app
```

Увеличьте лимиты памяти:

```bash
docker run -d \
  --name ai-chatbot-app \
  --env-file .env \
  -p 8000:8000 \
  --memory="10g" \
  --memory-swap="12g" \
  ai-chatbot:latest
```

## Production рекомендации

1. **Используйте .env с сильными паролями**
2. **Настройте reverse proxy (nginx)** для HTTPS
3. **Ограничьте ресурсы**:
   ```bash
   docker run -d \
     --name ai-chatbot-app \
     --env-file .env \
     -p 8000:8000 \
     --cpus="4" \
     --memory="10g" \
     --restart always \
     ai-chatbot:latest
   ```
4. **Используйте Docker volumes** для персистентности
5. **Мониторинг логов**: интегрируйте с системами логирования
6. **Регулярные бэкапы БД**

## Остановка всех сервисов

```bash
docker stop ai-chatbot-app
docker rm ai-chatbot-app
```

---

Готово! Приложение работает в Docker контейнере 🐳
