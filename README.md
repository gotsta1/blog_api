# Blog API with Redis Caching

REST API для блога на FastAPI с кешированием постов в Redis.

## Технологический стек

- **Python 3.12** / **FastAPI** / **Uvicorn**
- **PostgreSQL 15** — основное хранилище
- **Redis 7** — кеш для постов
- **SQLAlchemy 2.x** (async) — ORM
- **pytest** + **httpx** — интеграционные тесты

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone <repo-url>
cd blog_api
cp .env.example .env
```

### 2. Запустить через Docker

```bash
docker-compose up -d --build
```

Swagger UI доступен по адресу: http://localhost:8000/docs

### 3. Запустить тесты

```bash
docker-compose exec app pytest tests/ -v
```

## API эндпоинты

| Метод  | URL             | Описание                          |
|--------|-----------------|-----------------------------------|
| POST   | /posts          | Создать пост                      |
| GET    | /posts          | Список постов (пагинация)         |
| GET    | /posts/{id}     | Получить пост (с кешированием)    |
| PUT    | /posts/{id}     | Обновить пост (инвалидация кеша)  |
| DELETE | /posts/{id}     | Удалить пост (инвалидация кеша)   |

## Примеры запросов

```bash
# Создать пост
curl -X POST http://localhost:8000/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "Hello", "content": "World"}'

# Получить пост (первый запрос — из БД, последующие — из кеша)
curl http://localhost:8000/posts/1

# Обновить пост
curl -X PUT http://localhost:8000/posts/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'

# Удалить пост
curl -X DELETE http://localhost:8000/posts/1
```
