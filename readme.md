# Chat Backend API

Backend-сервис для чат-приложения. Архитектура построена на принципах Domain-Driven Design с четким разделением слоев и изоляцией бизнес-логики. Система предоставляет REST API для аутентификации, управления пользователями и загрузки файлов.

## Технологический стек

- **Python 3.13** с асинхронной поддержкой
- **FastAPI** — современный веб-фреймворк
- **PostgreSQL** — реляционная база данных
- **SQLAlchemy 2.0** — ORM с async поддержкой
- **Alembic** — миграции базы данных
- **MinIO** — S3-совместимое объектное хранилище для файлов
- **JWT аутентификация** — access/refresh токены через cookies
- **Docker & Docker Compose** — контейнеризация
- **Pydantic Settings** — управление конфигурацией
- **Type hints** — полная типизация во всех слоях

## Архитектура

Проект разделен на четыре слоя согласно принципам DDD:

- **Domain** (`app/domain/`) — бизнес-логика, сущности, value objects, доменные сервисы и интерфейсы
- **Application** (`app/application/`) — use cases через CQRS (Commands/Queries) и Mediator pattern
- **Infrastructure** (`app/infrastructure/`) — SQLAlchemy модели, репозитории, конвертеры, миграции, S3 клиент
- **Presentation** (`app/presentation/`) — FastAPI роуты, схемы запросов/ответов, обработка ошибок

### Dependency Injection

Реализован через контейнер `punq`. Все зависимости (репозитории, доменные сервисы, command/query handlers) регистрируются в контейнере и автоматически инжектируются в handlers через конструкторы. Контейнер создается один раз при старте приложения и используется во всех эндпоинтах через FastAPI `Depends`.

### CQRS Pattern

Применяется паттерн Command Query Responsibility Segregation:
- **Commands** — операции изменения состояния (создание пользователя, загрузка аватара)
- **Queries** — операции чтения данных (получение пользователя, аутентификация)
- **Mediator** — централизованная обработка команд и запросов

## Модель данных

### User

- `oid` — UUID (первичный ключ)
- `email` — строка (уникальный, валидация через EmailValueObject)
- `hashed_password` — строка (bcrypt хеш)
- `name` — строка (валидация через UserNameValueObject)
- `avatar_path` — строка (путь к файлу в S3, nullable)
- `last_online_at` — timestamp (nullable)
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
  - Требует аутентификацию (access token в cookies)
  - Response: данные пользователя с `avatar_url`
  
- `POST /api/v1/users/avatar` — загрузка аватара пользователя
  - Требует аутентификацию
  - Body: multipart/form-data с файлом
  - Автоматически генерирует случайное имя файла (UUID + расширение)
  - Сохраняет файл в MinIO по пути `avatars/{user_id}/{filename}`
  - Response: обновленные данные пользователя

### Healthcheck

- `GET /healthcheck` — проверка работоспособности сервиса

## Хранилище файлов

Система использует **MinIO** (S3-совместимое хранилище) для хранения файлов пользователей:

- Аватары сохраняются в bucket `chat-storage`
- Путь к файлу: `avatars/{user_id}/{random_uuid}.{extension}`
- Файлы доступны через presigned URLs (если требуется)

### Настройка MinIO

- **API порт**: 9000
- **Консоль порт**: 9001
- **Доступ**: http://localhost:9001
- **Логин по умолчанию**: `minioadmin` / `minioadmin`

## Бизнес-правила

### Валидация пароля

- Минимальная длина: 8 символов
- Должен содержать хотя бы одну букву и одну цифру

### Валидация email

- Проверка формата через `EmailValueObject`

### Загрузка аватара

- Файл загружается в S3 хранилище
- Генерируется случайное имя файла для безопасности
- Путь сохраняется в базе данных в поле `avatar_path`
- Старый аватар перезаписывается при новой загрузке

## Тестирование

Проект включает полное покрытие тестами:

- **Unit-тесты** доменной логики (value objects, entities, services)
- **Integration тесты** API через FastAPI TestClient
- **Mock хранилище** для тестов (DummyFileStorage)

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
  - 409 — конфликт (например, дубликат email)
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

# 2. Запуск всех сервисов (PostgreSQL, MinIO, приложение)
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
| `make all` | Запуск всех сервисов (приложение + PostgreSQL + MinIO) |
| `make all-down` | Остановка всех сервисов |
| `make app-up` | Запуск только приложения |
| `make app-down` | Остановка приложения |
| `make storages` | Запуск только хранилищ (PostgreSQL + MinIO) |
| `make storages-down` | Остановка хранилищ |

### Миграции

| Команда | Описание |
|---------|----------|
| `make migrations` | Создание новой миграции (autogenerate) |
| `make migrate` | Применение миграций (upgrade head) |

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