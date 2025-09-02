# 📚 Morphik - Полная документация системы
*Актуальная версия: 0.4.12 | Дата обновления: 02.09.2025*

## 📋 Оглавление
- [Обзор системы](#обзор-системы)
- [Архитектура](#архитектура)
- [Компоненты](#компоненты)
- [Структура проекта](#структура-проекта)
- [Запуск системы](#запуск-системы)
- [Доступ к сервисам](#доступ-к-сервисам)
- [Конфигурация](#конфигурация)
- [API Endpoints](#api-endpoints)
- [Решение проблем](#решение-проблем)

---

## 🎯 Обзор системы

Morphik - это распределенная система обработки документов с AI, использующая гибридную архитектуру с локальными и удаленными компонентами.

### Основные возможности
- 📄 **Обработка документов**: PDF, DOCX, изображения и другие форматы
- 🔍 **Мультимодальный поиск**: Поиск по тексту и визуальному содержимому с ColPali
- 💬 **AI чат**: Контекстно-зависимые диалоги с документами
- 🕸️ **Графы знаний**: Автоматическое извлечение сущностей и связей
- 🏠 **Локальные LLM**: Работа офлайн с Ollama
- 🚀 **GPU обработка**: ColPali serverless GPU для визуального анализа PDF
- 🔒 **Безопасность**: JWT аутентификация с SHA256+salt
- 💰 **Экономичность**: Pay-per-use GPU масштабирование

---

## 🏗️ Архитектура

### Текущее состояние (02.09.2025)
- **API и Worker**: Запускаются локально в Docker
- **UI**: Запускается в Docker (production build)
- **Тяжелые сервисы**: На удаленном сервере 135.181.106.12
- **ColPali GPU**: Serverless на Modal.com для обработки изображений
- **MinIO Storage**: S3-совместимое хранилище на сервере (порт 32000)
- **Единый пользователь**: demotest (ID: 8)

### Схема взаимодействия

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   Local API     │    │  Modal.com      │
│  (localhost:    │───▶│  (localhost:    │───▶│   (ColPali)     │
│     3000)       │    │     8000)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Hetzner       │    │   Auto-scaling  │
                       │ (135.181.106.12)│    │   (idle → off)  │
                       │                 │    └─────────────────┘
                       │ • PostgreSQL    │
                       │ • Redis         │
                       │ • Ollama        │
                       │ • MinIO         │
                       └─────────────────┘
```

### Распределение компонентов

| Компонент | Расположение | Порт | Описание |
|-----------|--------------|------|----------|
| UI | Локально (Docker) | 3000 | Next.js production build |
| API | Локально (Docker) | 8000 | FastAPI сервер |
| Worker | Локально (Docker) | - | Arq worker для фоновых задач |
| PostgreSQL | Hetzner | 5432 | База данных с pgvector |
| Redis | Hetzner | 6379 | Кеш и очереди задач |
| Ollama | Hetzner | 11434 | LLM модели (llama3.2:3b) |
| MinIO | Hetzner | 32000 | S3-совместимое хранилище |
| ColPali | Modal.com | HTTPS | Обработка изображений (serverless) |

---

## 🔧 Компоненты

### API (morphik_local-morphik)
- **Образ**: 3GB
- **Технологии**: FastAPI, Python 3.11, UV
- **Функции**:
  - REST API endpoints
  - JWT аутентификация
  - CORS для локальной разработки
  - Интеграция с LLM через LiteLLM

### Worker (morphik_local-worker)
- **Образ**: 3GB
- **Технологии**: Arq, Redis
- **Функции**:
  - Обработка документов
  - Индексация в векторную БД
  - Фоновые задачи

### UI (morphik_local-ui)
- **Образ**: 201MB
- **Технологии**: Next.js 14, React, TypeScript
- **Функции**:
  - Чат интерфейс
  - Управление документами
  - Визуализация графов
  - PDF viewer

### ColPali (Modal.com GPU)
- **Технологии**: vidore/colpali
- **Функции**:
  - Обработка изображений в PDF
  - Визуальное понимание таблиц, графиков
  - Векторизация для поиска
  - Автоматическое масштабирование

### MinIO Storage
- **Endpoint**: http://135.181.106.12:32000
- **Bucket**: morphik-storage
- **Функции**:
  - S3-совместимое хранилище
  - Хранение документов
  - Масштабируемость

---

## 📂 Структура проекта

```
Morphik_local/Test/Morphik_local/
├── core/                       # Backend API (FastAPI)
│   ├── api.py                 # Основные endpoints
│   ├── database/              # Работа с БД
│   ├── embedding/             # Векторизация
│   ├── storage/               # S3/MinIO интеграция
│   └── services/              # Бизнес-логика
│
├── ee/                        # Enterprise Edition
│   └── ui-component/          # Frontend (Next.js)
│       ├── components/        # React компоненты
│       ├── pages/            # Страницы
│       └── public/           # Статика
│
├── worker/                    # Фоновые задачи
├── auth-service/             # Сервис аутентификации
│
├── docker-compose.local.yml  # Основная конфигурация Docker
├── morphik.toml              # Конфигурация моделей
├── .env                      # Переменные окружения
└── storage/                  # Загруженные документы
```

---

## 🚀 Запуск системы

### Предварительные требования
- Docker Desktop
- Git
- 8GB RAM минимум
- 20GB свободного места

### Пошаговая инструкция

#### 1. Переход в рабочую директорию
```bash
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_local/Test/Morphik_local
```

#### 2. Запуск всех сервисов
```bash
# Остановить существующие контейнеры
docker-compose -f docker-compose.local.yml down

# Запустить все сервисы
docker-compose -f docker-compose.local.yml up -d

# Проверить статус
docker ps
```

#### 3. Проверка работоспособности
- **UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Здоровье**: `curl http://localhost:8000/health`

### Остановка системы
```bash
docker-compose -f docker-compose.local.yml down
```

---

## 🔐 Доступ к сервисам

### Локальные сервисы
- **Frontend UI**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Учетные данные по умолчанию
- **Username**: `demotest`
- **Password**: `demo`
- **Email**: `demotest@test.com`
- **User ID**: `8`

### Удаленные сервисы (135.181.106.12)
- **PostgreSQL**: порт 5432 (внутренний)
- **Redis**: порт 6379 (внутренний)
- **Ollama**: порт 11434 (внутренний)
- **MinIO**: порт 32000

### Modal.com (ColPali)
- **Endpoint**: Автоматически определяется
- **API Key**: Настроен в переменных окружения
- **Функция**: Визуальная обработка PDF

---

## ⚙️ Конфигурация

### Основные файлы

#### 1. `docker-compose.local.yml`
```yaml
services:
  morphik:
    build: .
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_URI=postgresql+asyncpg://morphik:morphik@135.181.106.12:5432/morphik
      - REDIS_HOST=135.181.106.12
      - OLLAMA_BASE_URL=http://135.181.106.12:11434
      - AWS_ACCESS_KEY_ID=uvqsdyUADcc1Uygu298j
      - AWS_SECRET_ACCESS_KEY=3jwYrh9tIstk9EL8vmLMfnZwRqHdzssGfRR391or
      - AWS_ENDPOINT_URL=http://135.181.106.12:32000
```

#### 2. `morphik.toml`
```toml
[registered_models]
ollama_llama = { model_name = "ollama/llama3.2:3b", api_base = "http://135.181.106.12:11434" }
ollama_embedding = { model_name = "ollama/nomic-embed-text", api_base = "http://135.181.106.12:11434" }

[completion]
model = "ollama_llama"

[embedding]
model = "ollama_embedding"
```

#### 3. `.env`
```env
AWS_ACCESS_KEY_ID=uvqsdyUADcc1Uygu298j
AWS_SECRET_ACCESS_KEY=3jwYrh9tIstk9EL8vmLMfnZwRqHdzssGfRR391or
AWS_ENDPOINT_URL=http://135.181.106.12:32000
S3_BUCKET_NAME=morphik-storage
```

---

## 🌐 API Endpoints

### Аутентификация
- `POST /auth/register` - Регистрация пользователя
- `POST /auth/login` - Вход в систему
- `GET /auth/me` - Текущий пользователь

### Модели
- `GET /v1/models` - Список доступных моделей
- `POST /v1/chat/completions` - Чат с AI

### Документы
- `POST /v1/ingest/files` - Загрузка документов
- `GET /v1/documents` - Список документов
- `POST /v1/retrieve` - Поиск по документам
- `DELETE /v1/documents/{id}` - Удаление документа

### Чаты
- `GET /v1/chats` - История чатов
- `POST /v1/chats` - Создать чат
- `GET /v1/chats/{id}` - Получить чат

---

## 🤖 Управление моделями

### Доступные модели
1. **Ollama модели** (всегда доступны):
   - `ollama/llama3.2:3b` - основная модель
   - `ollama/nomic-embed-text` - для векторизации

2. **Внешние модели** (требуют API ключи):
   - Claude (Anthropic)
   - GPT-4 (OpenAI)
   - Gemini (Google)

### Добавление моделей
1. Откройте Settings в UI
2. Добавьте API ключ провайдера
3. Модели появятся в списке выбора

---

## 🔍 Решение проблем

### CORS ошибки
```bash
# Проверьте что API запущен
docker logs morphik_local-morphik-1
```

### Подключение к БД
```bash
# Проверьте доступность сервера
nc -zv 135.181.106.12 5432  # PostgreSQL
nc -zv 135.181.106.12 6379  # Redis
nc -zv 135.181.106.12 11434 # Ollama
nc -zv 135.181.106.12 32000 # MinIO
```

### Docker контейнеры не запускаются
```bash
# Просмотр логов
docker-compose -f docker-compose.local.yml logs

# Пересборка образов
docker-compose -f docker-compose.local.yml build --no-cache
docker-compose -f docker-compose.local.yml up -d
```

### UI не подключается к API
```bash
# Проверьте переменные окружения
docker exec morphik_local-ui-1 env | grep API_URL
```

---

## 📊 Мониторинг

### Просмотр логов
```bash
# API логи
docker logs -f morphik_local-morphik-1

# Worker логи
docker logs -f morphik_local-worker-1

# UI логи
docker logs -f morphik_local-ui-1
```

### Использование ресурсов
```bash
# CPU и память
docker stats

# Размер образов
docker images | grep morphik
```

---

## 🛠️ Полезные команды

### Docker
```bash
# Перезапуск сервиса
docker-compose -f docker-compose.local.yml restart morphik

# Выполнение команды в контейнере
docker exec -it morphik_local-morphik-1 bash

# Очистка неиспользуемых ресурсов
docker system prune -a
```

### Проверка сервисов
```bash
# API здоровье
curl http://localhost:8000/health

# Список моделей
curl http://localhost:8000/v1/models \
  -H "Authorization: Bearer YOUR_TOKEN"

# MinIO статус
curl http://135.181.106.12:32000/minio/health/live
```

---

## 📝 Последние изменения (v0.4.12)

### ✅ Что добавлено
- Интеграция MinIO S3 хранилища
- Поддержка endpoint_url для S3-совместимых хранилищ
- ColPali через Modal.com для визуальной обработки
- Исправлены проблемы с AWS credentials

### 🔧 Что исправлено
- Ошибки 403 Forbidden при загрузке файлов
- Совместимость AWS_ACCESS_KEY vs AWS_ACCESS_KEY_ID
- Очистка базы от старых документов
- UI теперь в Docker (не npm dev)

---

## 📚 Дополнительные ресурсы

- **GitHub**: https://github.com/We-are-Humans-Corp/morphik_local_03
- **Основной Changelog**: Test/Morphik_local/MORPHIK_CHANGELOG.md
- **Файл очистки**: CLEANUP_PRIORITY.md

---

*Последнее обновление: 02.09.2025 | Версия: 0.4.12*