# AI Chat Bot 🤖

Интеллектуальный чат-бот на базе Ollama (LLaMA 3) с персонализацией, аутентификацией и сохранением истории разговоров.

## Особенности

✨ **Персонализация**: Бот запоминает информацию о пользователе и персонализирует общение  
🔐 **Аутентификация**: JWT-токены для безопасного доступа  
💾 **История чатов**: Сохранение всех разговоров в PostgreSQL  
👤 **Профиль пользователя**: Детальная информация и личные факты о пользователе  
🎯 **Расширяемая архитектура**: Модульная структура для легкого добавления новых сервисов  
🚀 **REST API**: Полноценный API для интеграции  
📱 **Telegram Bot**: Полная интеграция с Telegram мессенджером  
🌐 **Мультиязычность**: Автоматическое определение и поддержка 6 языков  

## Режимы работы

Бот поддерживает два режима:

1. **REST API** - HTTP API для интеграции в веб-приложения
2. **Telegram Bot** - Полнофункциональный бот для Telegram

Оба режима используют одну базу данных и одинаковую логику персонализации.

## Архитектура

Проект построен с использованием модульной архитектуры:

```
chat-bot/
├── app/
│   ├── api/              # REST API endpoints
│   │   ├── auth.py       # Аутентификация
│   │   ├── chat.py       # Чат
│   │   ├── user.py       # Профиль пользователя
│   │   └── dependencies.py
│   ├── telegram/         # Telegram bot
│   │   ├── handlers.py   # Обработчики команд и сообщений
│   │   └── __init__.py
│   ├── models/           # SQLAlchemy модели
│   │   └── user.py       # User, UserDetails, PersonalFact, ChatHistory
│   ├── services/         # Бизнес-логика (расширяемая)
│   │   ├── base.py       # BaseService для расширения
│   │   ├── auth_service.py
│   │   ├── ollama_service.py
│   │   ├── database_service.py
│   │   └── telegram_service.py  # Telegram интеграция
│   ├── config.py         # Конфигурация
│   ├── database.py       # Подключение к БД
│   ├── schemas.py        # Pydantic схемы
│   └── main.py           # FastAPI приложение
├── telegram_bot.py       # Точка входа Telegram бота
├── setup.sh              # Скрипт установки
├── start.sh              # Скрипт запуска REST API
├── start_telegram.sh     # Скрипт запуска Telegram бота
├── requirements.txt      # Python зависимости
├── README.md             # Основная документация
└── TELEGRAM_README.md    # Документация Telegram бота
```

## Требования

- Python 3.12.3+
- PostgreSQL
- Ollama
- Linux/macOS/WSL

## Установка

### 1. Клонирование и настройка

```bash
cd /home/dmitrylil/workspace/LTS-AAI/chat-bot
```

### 2. Настройка базы данных PostgreSQL

Создайте базу данных:

```bash
sudo -u postgres psql
CREATE DATABASE postgres;
CREATE USER chatbot_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;
\q
```

### 3. Настройка конфигурации

Отредактируйте файл `.env-tmp`:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=chatbot_db
DB_USER=chatbot_user
DB_PASSWORD=your_secure_password

# Ollama Configuration
OLLAMA_MODEL=llama3:8b
OLLAMA_BASE_URL=http://localhost:11434

# Application Configuration
SECRET_KEY=your-secret-key-change-this-in-production
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Language Configuration
DEFAULT_LANGUAGE=russian

# Telegram Bot Configuration (опционально)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_ADMIN_IDS=
```

### 4. Запуск установки

Скрипт автоматически:
- Проверит установку Ollama (если нет - установит)
- Скачает модель LLaMA 3:8b (если не скачана)
- Создаст виртуальное окружение Python
- Установит все зависимости

```bash
chmod +x setup.sh start.sh
./setup.sh
```

## Запуск

### REST API

```bash
./start.sh
```

Приложение будет доступно по адресу: `http://localhost:8000`

API документация (Swagger): `http://localhost:8000/docs`

### Telegram Bot

Полная документация: [TELEGRAM_README.md](TELEGRAM_README.md)

1. Получите токен от [@BotFather](https://t.me/BotFather) в Telegram
2. Добавьте токен в `.env`:
   ```bash
   TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
   ```
3. Запустите бота:
   ```bash
   ./start_telegram.sh
   ```

Оба режима (REST API и Telegram Bot) могут работать одновременно!

## API Endpoints

### Аутентификация

#### Регистрация
```bash
POST /auth/register
{
  "username": "john_doe",
  "password": "secure_password123"
}
```

#### Вход
```bash
POST /auth/login
{
  "username": "john_doe",
  "password": "secure_password123"
}
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Профиль пользователя

Все запросы требуют заголовок: `Authorization: Bearer <token>`

#### Создать/обновить детали пользователя
```bash
POST /user/details
{
  "full_name": "Иван Иванов",
  "email": "ivan@example.com",
  "phone": "+7-999-123-45-67",
  "bio": "Любитель технологий и путешествий"
}
```

#### Добавить личный факт
```bash
POST /user/facts
{
  "fact_key": "hobby",
  "fact_value": "Играю на гитаре и люблю рок-музыку"
}

POST /user/facts
{
  "fact_key": "birthday",
  "fact_value": "15 марта 1995"
}
```

#### Получить все факты
```bash
GET /user/facts
```

### Чат

#### Начать новую сессию
```bash
POST /chat/start
Authorization: Bearer <token>
```

Ответ:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Привет, Иван! 👋 Как твои дела? Чем могу помочь сегодня?",
  "timestamp": "2025-11-18T10:30:00"
}
```

#### Отправить сообщение
```bash
POST /chat/message?session_id=<session_id>
Authorization: Bearer <token>
{
  "message": "Посоветуй мне интересную книгу"
}
```

#### Получить историю
```bash
GET /chat/history/<session_id>
Authorization: Bearer <token>
```

#### Получить все сессии пользователя
```bash
GET /chat/sessions
Authorization: Bearer <token>
```

## Примеры использования

### Полный сценарий

```bash
# 1. Регистрация
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "ivan", "password": "mypassword123"}'

# 2. Вход
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "ivan", "password": "mypassword123"}' \
  | jq -r '.access_token')

# 3. Добавить информацию о себе
curl -X POST http://localhost:8000/user/details \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Иван Петров",
    "bio": "Программист, люблю Python и AI"
  }'

# 4. Добавить хобби
curl -X POST http://localhost:8000/user/facts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fact_key": "hobby", "fact_value": "Программирование и шахматы"}'

# 5. Начать чат
SESSION=$(curl -X POST http://localhost:8000/chat/start \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.session_id')

# 6. Отправить сообщение
curl -X POST "http://localhost:8000/chat/message?session_id=$SESSION" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Расскажи про Python"}'
```

## База данных

### Таблицы

**users** - Основная таблица пользователей
- id, username, password_hash, created_at, updated_at

**user_details** - Детальная информация о пользователе
- id, user_id, full_name, email, phone, bio, created_at, updated_at

**personal_facts** - Личные факты о пользователе
- id, user_id, fact_key, fact_value, created_at, updated_at

**chat_history** - История сообщений
- id, user_id, session_id, role (user/assistant), message, created_at

## Персонализация

Бот использует всю доступную информацию о пользователе:
- Имя из user_details
- Биографию
- Личные факты (хобби, день рождения, предпочтения и т.д.)

Эта информация передается в системный промпт модели, что позволяет боту:
- Обращаться к пользователю по имени
- Учитывать его интересы в ответах
- Вести более естественный и персонализированный диалог

## Расширение функционала

### Добавление нового сервиса

1. Создайте новый сервис, наследуясь от `BaseService`:

```python
# app/services/my_service.py
from app.services.base import BaseService

class MyService(BaseService):
    async def initialize(self) -> bool:
        # Инициализация
        return True
    
    async def health_check(self) -> bool:
        # Проверка здоровья
        return True
    
    async def my_method(self):
        # Ваша логика
        pass

my_service = MyService()
```

2. Используйте сервис в API endpoints

### Добавление новых endpoints

Создайте новый роутер в `app/api/`:

```python
from fastapi import APIRouter
router = APIRouter(prefix="/my-endpoint", tags=["My Feature"])

@router.get("/")
async def my_endpoint():
    return {"message": "Hello"}
```

Подключите в `main.py`:
```python
from app.api import my_router
app.include_router(my_router.router)
```

## Troubleshooting

### Ollama не запускается
```bash
# Проверьте статус
systemctl status ollama

# Запустите вручную
ollama serve
```

### Модель не найдена
```bash
# Скачайте модель вручную
ollama pull llama3:8b
```

### Ошибки базы данных
```bash
# Проверьте подключение
psql -h localhost -U chatbot_user -d chatbot_db
```

### Проверка здоровья системы
```bash
curl http://localhost:8000/health
```

## Производительность

- **Модель**: LLaMA 3:8B требует ~8GB RAM
- **База данных**: Рекомендуется PostgreSQL 13+
- **API**: FastAPI с async поддержкой для высокой производительности

## Безопасность

⚠️ **Важно для production:**

1. Измените `SECRET_KEY` и `JWT_SECRET_KEY` в `.env-tmp`
2. Используйте сильные пароли для БД
3. Настройте CORS в `main.py` для конкретных доменов
4. Используйте HTTPS
5. Настройте rate limiting
6. Регулярно обновляйте зависимости

## Лицензия

MIT

## Поддержка

При возникновении проблем создайте issue с описанием:
- Версия Python
- Версия Ollama
- Логи ошибок
- Шаги для воспроизведения

---

Создано с ❤️ используя FastAPI, Ollama и PostgreSQL
