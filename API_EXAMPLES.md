# API Testing Examples

Примеры запросов для тестирования API

## Переменные окружения

```bash
export API_URL="http://localhost:8000"
```

## 1. Регистрация нового пользователя

```bash
curl -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "TestPass123"
  }'
```

## 2. Вход в систему

```bash
curl -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "TestPass123"
  }'
```

Сохраните токен:
```bash
TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "TestPass123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"
```

## 3. Создание профиля пользователя

```bash
curl -X POST "$API_URL/user/details" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Дмитрий Петров",
    "email": "dmitry@example.com",
    "phone": "+7-999-123-45-67",
    "bio": "Разработчик на Python, увлекаюсь AI и машинным обучением"
  }'
```

## 4. Добавление личных фактов

```bash
# Хобби
curl -X POST "$API_URL/user/facts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fact_key": "hobby",
    "fact_value": "Программирование, чтение научной фантастики, бег"
  }'

# День рождения
curl -X POST "$API_URL/user/facts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fact_key": "birthday",
    "fact_value": "15 июля 1992"
  }'

# Любимая еда
curl -X POST "$API_URL/user/facts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fact_key": "favorite_food",
    "fact_value": "Суши и итальянская паста"
  }'

# Домашние животные
curl -X POST "$API_URL/user/facts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fact_key": "pets",
    "fact_value": "Есть кот по имени Барсик"
  }'
```

## 5. Просмотр профиля

```bash
# Получить детали
curl -X GET "$API_URL/user/details" \
  -H "Authorization: Bearer $TOKEN"

# Получить все факты
curl -X GET "$API_URL/user/facts" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## 6. Начало чата (с приветствием)

```bash
SESSION_ID=$(curl -s -X POST "$API_URL/chat/start" \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.session_id')

echo "Session ID: $SESSION_ID"

# Посмотреть приветствие
curl -X POST "$API_URL/chat/start" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## 7. Отправка сообщений

```bash
# Сообщение 1
curl -X POST "$API_URL/chat/message?session_id=$SESSION_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Привет! Как дела?"
  }' | jq

# Сообщение 2
curl -X POST "$API_URL/chat/message?session_id=$SESSION_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Что ты можешь рассказать про Python?"
  }' | jq

# Сообщение 3 (с учетом персонализации)
curl -X POST "$API_URL/chat/message?session_id=$SESSION_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Посоветуй мне книгу про AI, учитывая мои интересы"
  }' | jq
```

## 8. Просмотр истории

```bash
curl -X GET "$API_URL/chat/history/$SESSION_ID" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## 9. Все сессии пользователя

```bash
curl -X GET "$API_URL/chat/sessions" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## 10. Обновление личного факта

```bash
curl -X PUT "$API_URL/user/facts/hobby" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fact_value": "Программирование, чтение, бег и фотография"
  }'
```

## 11. Удаление личного факта

```bash
curl -X DELETE "$API_URL/user/facts/pets" \
  -H "Authorization: Bearer $TOKEN"
```

## 12. Проверка здоровья системы

```bash
curl -X GET "$API_URL/health" | jq
```

## Полный тестовый сценарий

```bash
#!/bin/bash

# Настройки
API_URL="http://localhost:8000"
USERNAME="test_$(date +%s)"
PASSWORD="TestPass123"

echo "=== Регистрация ==="
curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}" | jq

echo -e "\n=== Вход ==="
TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}" \
  | jq -r '.access_token')

echo "Token получен: ${TOKEN:0:20}..."

echo -e "\n=== Создание профиля ==="
curl -s -X POST "$API_URL/user/details" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Тестовый Пользователь",
    "bio": "Люблю тестировать новые API"
  }' | jq

echo -e "\n=== Добавление фактов ==="
curl -s -X POST "$API_URL/user/facts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fact_key": "hobby", "fact_value": "Тестирование"}' | jq

echo -e "\n=== Начало чата ==="
START_RESPONSE=$(curl -s -X POST "$API_URL/chat/start" \
  -H "Authorization: Bearer $TOKEN")

echo "$START_RESPONSE" | jq

SESSION_ID=$(echo "$START_RESPONSE" | jq -r '.session_id')

echo -e "\n=== Отправка сообщения ==="
curl -s -X POST "$API_URL/chat/message?session_id=$SESSION_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Расскажи про себя"}' | jq

echo -e "\n=== История чата ==="
curl -s -X GET "$API_URL/chat/history/$SESSION_ID" \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\n=== Тест завершен ==="
```

Сохраните этот скрипт как `test_api.sh` и запустите:
```bash
chmod +x test_api.sh
./test_api.sh
```
