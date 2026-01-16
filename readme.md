# Chat Backend API

Backend-сервис для чат-приложения. Архитектура построена на принципах Domain-Driven Design с четким разделением слоев и изоляцией бизнес-логики. Система предоставляет REST API для аутентификации, управления пользователями, чатами, сообщениями и real-time обновления через WebSocket.

## Технологический стек

- **Python 3.13** с асинхронной поддержкой
- **FastAPI** — современный веб-фреймворк
- **PostgreSQL** — реляционная база данных для пользователей
- **MongoDB** — документная база данных для чатов и сообщений
- **SQLAlchemy 2.0** — ORM с async поддержкой для PostgreSQL
- **Motor** — асинхронный драйвер для MongoDB
- **Alembic** — миграции базы данных
- **MinIO** — S3-совместимое объектное хранилище для файлов
- **JWT аутентификация** — access/refresh токены через cookies и headers
- **WebSocket** — real-time обновления для чатов
- **Docker & Docker Compose** — контейнеризация
- **Pydantic Settings** — управление конфигурацией
- **Type hints** — полная типизация во всех слоях

## Архитектура

Проект разделен на четыре слоя согласно принципам DDD:

- **Domain** (`app/domain/`) — бизнес-логика, сущности, value objects, доменные сервисы и интерфейсы
- **Application** (`app/application/`) — use cases через CQRS (Commands/Queries) и Mediator pattern
- **Infrastructure** (`app/infrastructure/`) — SQLAlchemy модели, MongoDB репозитории, конвертеры, миграции, S3 клиент, WebSocket менеджер
- **Presentation** (`app/presentation/`) — FastAPI роуты, схемы запросов/ответов, обработка ошибок, WebSocket endpoints

### Dependency Injection

Реализован через контейнер `punq`. Все зависимости (репозитории, доменные сервисы, command/query handlers) регистрируются в контейнере и автоматически инжектируются в handlers через конструкторы. Контейнер создается один раз при старте приложения и используется во всех эндпоинтах через FastAPI `Depends`.

### CQRS Pattern

Применяется паттерн Command Query Responsibility Segregation:
- **Commands** — операции изменения состояния (создание пользователя, чата, сообщения, загрузка аватара)
- **Queries** — операции чтения данных (получение пользователя, чата, сообщений, аутентификация)
- **Mediator** — централизованная обработка команд и запросов

## Модель данных

### User (PostgreSQL)

- `oid` — UUID (первичный ключ)
- `email` — строка (уникальный, валидация через EmailValueObject)
- `hashed_password` — строка (bcrypt хеш)
- `name` — строка (валидация через UserNameValueObject)
- `avatar_path` — строка (путь к файлу в S3, nullable)
- `last_online_at` — timestamp (nullable)
- `created_at` — timestamp
- `updated_at` — timestamp

### Chat (MongoDB)

- `oid` — UUID (первичный ключ)
- `title` — строка (1-255 символов, валидация через ChatTitleValueObject)
- `owner_id` — UUID (ID владельца чата)
- `created_at` — timestamp
- `updated_at` — timestamp

### Message (MongoDB)

- `oid` — UUID (первичный ключ)
- `chat_id` — UUID (ID чата)
- `sender_id` — UUID (ID отправителя)
- `content` — строка (1-4096 символов, валидация через MessageContentValueObject)
- `created_at` — timestamp
- `updated_at` — timestamp

## API эндпоинты

### Аутентификация (`/api/v1/auth`)

- `POST /api/v1/auth/register` — регистрация нового пользователя
  - Body: `{ email, password, name }`
  - Response: данные созданного пользователя
  
- `POST /api/v1/auth/login` — аутентификация и получение токенов
  - Body: `{ email, password }`
  - Response: `{ access_token, refresh_token }`
  - Устанавливает токены в cookies
  
- `POST /api/v1/auth/token/refresh` — обновление access токена
  - Использует refresh token из cookies
  - Response: новый `access_token`

### Пользователи (`/api/v1/users`)

- `GET /api/v1/users/me` — получение информации о текущем пользователе
  - Требует аутентификацию (access token в cookies или Authorization header)
  - Response: данные пользователя с `avatar_url`
  
- `POST /api/v1/users/avatar` — загрузка аватара пользователя
  - Требует аутентификацию
  - Body: multipart/form-data с файлом
  - Автоматически генерирует случайное имя файла (UUID + расширение)
  - Сохраняет файл в MinIO по пути `avatars/{user_id}/{filename}`
  - Response: обновленные данные пользователя

### Чаты (`/api/v1/chats`)

- `POST /api/v1/chats` — создание нового чата
  - Требует аутентификацию
  - Body: `{ title: str }`
  - Response: данные созданного чата
  - Владелец чата определяется автоматически из токена

- `GET /api/v1/chats/{chat_id}` — получение чата по ID
  - Response: данные чата

- `DELETE /api/v1/chats/{chat_id}` — удаление чата
  - Требует аутентификацию
  - Response: 204 No Content

### Сообщения (`/api/v1/chats/{chat_id}/messages`)

- `POST /api/v1/chats/{chat_id}/messages` — создание нового сообщения
  - Требует аутентификацию
  - Body: `{ content: str }`
  - Response: данные созданного сообщения
  - Автоматически отправляет уведомление всем подключенным к чату клиентам через WebSocket
  - Отправитель определяется автоматически из токена

- `GET /api/v1/chats/{chat_id}/messages` — получение сообщений чата с пагинацией
  - Query параметры:
    - `limit` (default: 10, min: 1, max: 100) — количество сообщений
    - `offset` (default: 0, min: 0) — смещение для пагинации
  - Response: `{ items: Message[], total: int }`
  - Сообщения отсортированы по дате создания (новые первыми)

### WebSocket (`/api/v1/chats/{chat_oid}`)

- `WS /api/v1/chats/{chat_oid}` — подключение к чату для real-time обновлений
  - Требует аутентификацию через:
    - Cookie: `access_token=<token>`
    - Header: `Authorization: Bearer <token>`
  - При успешном подключении отправляет приветственное сообщение
  - При создании нового сообщения в чате все подключенные клиенты получают уведомление:
    ```json
    {
      "type": "new_message",
      "message": {
        "oid": "...",
        "chat_id": "...",
        "sender_id": "...",
        "content": "...",
        "created_at": "...",
        "updated_at": "..."
      }
    }
    ```

### Healthcheck

- `GET /healthcheck` — проверка работоспособности сервиса

## Real-time обновления

Система использует **WebSocket** для доставки новых сообщений в реальном времени:

## Бизнес-правила

### Валидация пароля

- Минимальная длина: 8 символов
- Должен содержать хотя бы одну букву и одну цифру

### Валидация email

- Проверка формата через `EmailValueObject`

### Валидация чата

- Название чата: от 1 до 255 символов
- Название чата должно быть уникальным

### Валидация сообщения

- Содержимое сообщения: от 1 до 4096 символов
- Не может быть пустым или содержать только пробелы

### Загрузка аватара

- Файл загружается в S3 хранилище
- Генерируется случайное имя файла для безопасности
- Путь сохраняется в базе данных в поле `avatar_path`
- Старый аватар перезаписывается при новой загрузке

## Тестирование

Проект включает полное покрытие тестами:

- **Unit-тесты** доменной логики (value objects, entities)
- **Integration тесты** use cases (commands, queries)
- **Mock хранилище** для тестов (DummyFileStorage, DummyInMemoryChatsRepository, DummyInMemoryMessagesRepository)

Запуск тестов:
```bash
make test
```

## Качество кода

- **Типизация** — полная типизация во всех публичных интерфейсах
- **Обработка ошибок** — централизованная обработка через exception handlers
  - 400 — ошибки валидации
  - 401 — неавторизован
  - 404 — ресурс не найден
  - 409 — конфликт (например, дубликат email или названия чата)
- **Линтер** — ruff + isort с pre-commit хуками
- **Форматирование** — black для единообразного стиля кода

## Запуск проекта

### Предварительные требования

- Docker и Docker Compose
- Python 3.13 (для локальной разработки)

### Быстрый старт

```bash
# 1. Копирование файла с переменными окружения
cp .env.example .env

# 2. Запуск всех сервисов (PostgreSQL, MongoDB, MinIO, приложение)
make all

# 3. Применение миграций базы данных
make migrate

# 4. Проверка работоспособности
curl http://localhost:8000/healthcheck
```

API документация доступна по адресу: **http://localhost:8000/api/docs**

## Основные команды

### Управление сервисами

| Команда | Описание |
|---------|----------|
| `make all` | Запуск всех сервисов (приложение + PostgreSQL + MongoDB + MinIO) |
| `make all-down` | Остановка всех сервисов |
| `make app-up` | Запуск только приложения |
| `make app-down` | Остановка приложения |
| `make storages` | Запуск только хранилищ (PostgreSQL + MongoDB + MinIO) |
| `make storages-down` | Остановка хранилищ |

### Миграции

| Команда | Описание |
|---------|----------|
| `make migrations` | Создание новой миграции (autogenerate) |
| `make migrate` | Применение миграций (upgrade head) |
| `make reapply-migrations` | Переприменение миграций (downgrade base + upgrade head) |

### Разработка

| Команда | Описание |
|---------|----------|
| `make test` | Запуск всех тестов |
| `make precommit` | Запуск pre-commit проверок для всех файлов |
| `make app-shell` | Подключение к контейнеру приложения |
| `make postgres` | Подключение к PostgreSQL через psql |

### Логи

| Команда | Описание |
|---------|----------|
| `make app-logs` | Просмотр логов приложения |
| `make storages-logs` | Просмотр логов хранилищ |


### Подключение к WebSocket

```javascript
// JavaScript пример
const ws = new WebSocket('ws://localhost:8000/api/v1/chats/{chat_id}', {
  headers: {
    'Authorization': 'Bearer <your_access_token>'
  }
});

ws.onopen = () => {
  console.log('Connected to chat');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'new_message') {
    console.log('New message:', data.message);
  }
};
```

## Структура проекта

```
app/
├── domain/              # Доменная логика
│   ├── chats/          # Доменная логика чатов
│   │   ├── entities/   # ChatEntity, MessageEntity
│   │   ├── value_objects/  # ChatTitleValueObject, MessageContentValueObject
│   │   ├── exceptions/ # Доменные исключения
│   │   └── interfaces/ # Интерфейсы репозиториев
│   └── users/          # Доменная логика пользователей
├── application/        # Use cases (CQRS)
│   ├── chats/          # Commands и Queries для чатов
│   └── users/          # Commands и Queries для пользователей
├── infrastructure/     # Инфраструктура
│   ├── database/      # Репозитории, модели, конвертеры
│   │   ├── repositories/
│   │   │   ├── chats/  # MongoDB репозитории для чатов
│   │   │   └── users/  # PostgreSQL репозитории для пользователей
│   │   └── migrations/ # Alembic миграции
│   ├── websockets/     # WebSocket connection manager
│   └── s3/             # S3 клиент и хранилище
└── presentation/       # API слой
    └── api/
        └── v1/
            ├── auth/   # Эндпоинты аутентификации
            ├── users/  # Эндпоинты пользователей
            └── chats/  # Эндпоинты чатов и WebSocket
```
