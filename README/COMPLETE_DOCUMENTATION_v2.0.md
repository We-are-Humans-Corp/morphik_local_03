# 📚 Morphik - Полная документация системы v2.0
## С интеграцией Modal.com GPU инфраструктуры

*Актуальная версия: 2.0 | Дата обновления: 11.01.2025*

## 📋 Оглавление
- [Обзор системы](#обзор-системы)
- [Архитектура v2.0](#архитектура-v20)
- [Компоненты системы](#компоненты-системы)
- [Структура проекта](#структура-проекта)
- [Workflow обработки документов](#workflow-обработки-документов)
- [Порты и endpoints](#порты-и-endpoints)
- [Запуск системы](#запуск-системы)
- [Конфигурация](#конфигурация)
- [API документация](#api-документация)
- [Мониторинг и диагностика](#мониторинг-и-диагностика)
- [Миграция с v1.0](#миграция-с-v10)

---

## 🎯 Обзор системы

Morphik v2.0 - это распределенная система обработки документов с AI, использующая трехуровневую архитектуру с локальными сервисами, удаленным сервером Hetzner и GPU инфраструктурой Modal.com.

### Ключевые изменения в v2.0
- ✅ **Modal.com GPU**: Serverless обработка ColPali на A100-40GB
- ✅ **Прямая запись в PostgreSQL**: Modal пишет embeddings напрямую в БД
- ✅ **Base64 хранение изображений**: В PostgreSQL вместо S3 путей
- ✅ **BFloat16 → Float32**: Автоматическая конвертация для сериализации
- ✅ **Увеличенные лимиты**: max_length=2048 для токенов
- ✅ **JWT с app_id**: Расширенная аутентификация

### Основные возможности
- 📄 **Мультимодальная обработка**: PDF с изображениями, таблицами, графиками
- 🚀 **ColPali v1.2**: Визуальное понимание документов на GPU
- 💬 **Multi-model чат**: GPT-4, Claude, Gemini, Ollama
- 🕸️ **Графы знаний**: Автоматическое извлечение сущностей
- 🔍 **Гибридный поиск**: Текст + визуальный контент
- 💰 **Pay-per-use GPU**: Экономия до 90% на инфраструктуре
- 🔒 **Enterprise безопасность**: JWT, app_id, user scoping

---

## 🏗️ Архитектура v2.0

### Трехуровневая архитектура

``` Реальная архитектура: UI локально, API на сервере с JWT auth и умной обработкой документов

┌─────────────────────────────────────────────────────────────┐
│                     ЛОКАЛЬНАЯ МАШИНА                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │   UI (React/Next.js) - Docker контейнер              │   │
│  │   Port: 3000                                         │   │
│  │   • Login/Register с реальной JWT аутентификацией    │   │
│  │   • Отправляет запросы на 135.181.106.12:8000       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬────────────────────────────────────┘
                         │ HTTP с JWT токеном
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              HETZNER SERVER (135.181.106.12)                 │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────┐     │
│  │ API (FastAPI) - Docker контейнер                   │     │
│  │ Port: 8000                                         │     │
│  │ • JWT токены с реальным user_id из БД             │     │
│  │ • Умная логика обработки документов:              │     │
│  │   - Текст (txt/md) → MorphikParser + Ollama       │     │
│  │   - Визуал (pdf/img) → ColPali через Modal.com    │     │
│  │ • Cross-domain CORS для localhost:3000            │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │Worker (Arq)  │  │    Redis     │      │
│  │  Port: 5432  │  │ Background   │  │  Port: 6379  │      │
│  │  • users     │  │ Processing   │  │  Cache/Queue │      │
│  │  • documents │  └──────────────┘  └──────────────┘      │
│  │  • embeddings│                                           │
│  └──────────────┘                                           │
│  ┌──────────────┐  ┌──────────────────────────────┐        │
│  │   Ollama     │  │        MinIO S3                │        │
│  │ Port: 11434  │  │      Port: 32000               │        │
│  │ • llama3.2   │  │   • morphik-storage bucket     │        │
│  │ • nomic-embed│  └──────────────────────────────┘        │
│  └──────────────┘                                           │
└─────────────────────────┬────────────────────────────────────┘
                         │ API calls (только для визуальных документов)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  MODAL.COM GPU CLOUD                        │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────┐     │
│  │  ColPali Processor (A100-40GB)                     │     │
│  │  • Endpoint: rugusev--morphik-processor-*          │     │
│  │  • Model: vidore/colpali-v1.2                      │     │
│  │  • Обрабатывает ТОЛЬКО изображения и PDF           │     │
│  │  • Direct PostgreSQL writes to Hetzner             │     │
│  │  • BFloat16 → Float32 conversion                   │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Полный workflow документа

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant UI as UI (3000)
    participant API as API (8000)
    participant W as Worker
    participant M as Modal GPU
    participant PG as PostgreSQL
    participant R as Redis

    U->>UI: Upload PDF
    UI->>API: POST /v1/ingest/files
    API->>PG: Create document record
    API->>R: Queue ingestion task
    API-->>UI: Return task_id
    
    R->>W: Pull task
    W->>W: Parse PDF to chunks
    W->>M: Send images for ColPali
    M->>M: Process with A100 GPU
    M->>M: Convert BFloat16→Float32
    M->>PG: Save embeddings directly
    M-->>W: Return success
    W->>PG: Update document status
    W->>R: Mark task complete
    
    U->>UI: Query document
    UI->>API: POST /v1/query
    API->>PG: Vector search
    API->>API: Rerank results
    API-->>UI: Return results
```

---

## 🔧 Компоненты системы

### Локальные компоненты (Docker)

#### 1. UI Service (morphik-ui-distributed)
- **Образ**: 201MB (production build)
- **Порт**: 3000
- **Технологии**: Next.js 15, React 19, TypeScript, ShadCN UI
- **Путь**: `/ee/ui-component`
- **Функции**:
  - Drag-and-drop загрузка документов
  - Real-time чат интерфейс
  - Визуализация графов знаний
  - PDF viewer с аннотациями
  - Управление моделями

#### 2. API Service (morphik-colpali-configured)
- **Образ**: 2.96GB
- **Порт**: 8000
- **Технологии**: FastAPI, Python 3.11, Pydantic v2
- **Путь**: `/core`
- **Функции**:
  - REST API endpoints
  - JWT аутентификация с app_id
  - WebSocket для real-time
  - OpenAPI документация
  - Интеграция с Modal.com

#### 3. Worker Service (включен в API контейнер)
- **Технологии**: Arq, asyncio, Redis
- **Путь**: `/core/workers`
- **Функции**:
  - Асинхронная обработка документов
  - Батчинг для Modal API
  - Управление очередями
  - Retry логика

### Modal.com компоненты

#### ColPali Processor
- **GPU**: NVIDIA A100-40GB
- **Memory**: 32GB RAM
- **Timeout**: 600 секунд
- **Endpoints**:
  ```
  Main: https://rugusev--morphik-processor-process-colpali.modal.run
  Health: https://rugusev--morphik-processor-health.modal.run
  ```
- **Модель**: vidore/colpali-v1.2
- **Особенности**:
  - Persistent model cache в `/models`
  - Auto-scaling (0 → N instances)
  - Direct PostgreSQL writes
  - BFloat16 → Float32 conversion

### Hetzner Server компоненты (135.181.106.12)

#### PostgreSQL (Port 5432)
- **Версия**: 16 с pgvector
- **База**: morphik
- **Основные таблицы**:
  ```sql
  -- Мультивекторные embeddings от ColPali
  multi_vector_embeddings:
    - document_id TEXT
    - chunk_number INTEGER  
    - content TEXT (Base64 images)
    - chunk_metadata JSONB
    - embeddings JSONB
    - PRIMARY KEY (document_id, chunk_number)
  
  -- Метаданные документов
  documents:
    - id SERIAL PRIMARY KEY
    - external_id TEXT UNIQUE
    - app_id TEXT
    - user_id INTEGER
    - title, content, metadata
  
  -- Пользователи
  users:
    - id SERIAL PRIMARY KEY
    - email TEXT UNIQUE
    - api_key TEXT
  ```

#### Redis (Port 6379)
- **Функции**: Кеш, очереди задач, sessions
- **Databases**:
  - DB 0: Arq task queue
  - DB 1: Cache
  - DB 2: Sessions

#### Ollama (Port 11434)
- **Модели**:
  - llama3.2:3b (основная)
  - nomic-embed-text (embeddings)
- **API**: OpenAI-compatible

#### MinIO (Port 32000)
- **Bucket**: morphik-storage
- **Access**: S3-compatible API
- **Используется**: Для больших файлов (не изображения)

---

## 📂 Структура проекта

```
/Users/fedor/PycharmProjects/PythonProject/Morphik_local/
├── hetzner-morphik/            # Полная копия с сервера (Backend + все сервисы)
│   ├── core/                   # Backend API
│   │   ├── api.py             # FastAPI application
│   │   ├── routes/            # API endpoints
│   │   │   └── auth.py       # JWT аутентификация
│   │   ├── services/          # Бизнес-логика
│   │   ├── models/            # SQLAlchemy модели
│   │   ├── embedding/         # Embedding провайдеры
│   │   │   └── colpali_api_embedding_model.py  # ColPali интеграция
│   │   ├── workers/           # Background workers
│   │   │   └── ingestion_worker.py  # Document processing
│   │   └── database/          # Database layer
│   │
│   ├── ee/ui-component/        # UI компоненты (копия для reference)
│   ├── docker-compose.yml     # Docker конфигурация сервера
│   ├── morphik.toml          # Основная конфигурация
│   └── .env                  # Environment переменные
│
├── morphik-ui/                 # Локальный UI в Docker
│   ├── ee/ui-component/        # Frontend React/Next.js
│   │   ├── app/               # Next.js app router
│   │   ├── components/        # React components
│   │   └── lib/              # Utilities
│   │
│   ├── docker-compose.yml     # Docker для UI
│   ├── docker-compose.override.yml  # Локальные override настройки
│   ├── dockerfile.ui          # Dockerfile для UI образа
│   └── .env                  # UI конфигурация
│
├── modal-morphik_test/         # Modal.com тесты и разработка
│   └── morphik_processor_fixed.py  # ColPali GPU processor
│
├── README/                     # Документация
│   ├── COMPLETE_DOCUMENTATION_v2.0.md  # Этот файл
│   └── COLPALI_COMPLETE_SETUP.md      # ColPali детали
│
└── .env                       # Основная конфигурация
```

---

## 🚦 Workflow обработки документов

### 1. Загрузка документа

```python
# UI → API
POST http://localhost:8000/v1/ingest/files
Content-Type: multipart/form-data

file: document.pdf
metadata: {"app_id": "morphik_app"}
```

### 2. Обработка в Worker

```python
# Worker процесс
async def process_document(doc_id: str):
    # 1. Парсинг документа
    chunks = await parser.parse(document)
    
    # 2. Разделение на text/image chunks  
    text_chunks = [c for c in chunks if not c.is_image]
    image_chunks = [c for c in chunks if c.is_image]
    
    # 3. Отправка изображений в Modal
    if image_chunks:
        await colpali_api.embed_for_ingestion(
            chunks=image_chunks,
            document_id=doc_id,
            start_index=0
        )
    
    # 4. Обработка текста локально
    if text_chunks:
        embeddings = await embed_text(text_chunks)
        await save_to_postgres(embeddings)
```

### 3. ColPali обработка на Modal.com

```python
# Modal GPU процесс
@app.function(gpu="A100", timeout=600)
def process_colpali(images: List[str], document_id: str, chunk_ids: List[int]):
    # 1. Загрузка модели (кешировано)
    model = ColPali.from_pretrained("vidore/colpali-v1.2")
    processor = AutoProcessor.from_pretrained(
        "vidore/colpali-v1.2",
        max_length=2048,
        truncation=False
    )
    
    # 2. Обработка изображений
    with torch.no_grad():
        outputs = model(**inputs)
        # ColPali возвращает tensor напрямую
        embeddings = outputs.mean(dim=1).to(torch.float32)
    
    # 3. Прямая запись в PostgreSQL
    conn = psycopg2.connect(
        host="135.181.106.12",
        database="morphik",
        user="morphik",
        password="morphik"
    )
    
    for i, (chunk_id, embedding) in enumerate(zip(chunk_ids, embeddings)):
        cur.execute("""
            INSERT INTO multi_vector_embeddings 
            (document_id, chunk_number, content, embeddings, chunk_metadata)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (document_id, chunk_number) 
            DO UPDATE SET embeddings = EXCLUDED.embeddings
        """, (
            document_id,
            chunk_id,
            f"data:image/png;base64,{images[i]}",
            json.dumps(embedding.tolist()),
            json.dumps({"model": "colpali-v1.2", "timestamp": now})
        ))
    
    conn.commit()
    return {"success": True, "processed": len(images)}
```

### 4. Поиск и retrieval

```python
# API endpoint
@router.post("/v1/query")
async def query_documents(query: QueryRequest):
    # 1. Генерация query embedding
    if query.use_colpali:
        query_embedding = await colpali_api.embed_query(query.text)
    else:
        query_embedding = await embed_text(query.text)
    
    # 2. Vector search в PostgreSQL
    results = await db.execute("""
        SELECT document_id, chunk_number, content,
               1 - (embeddings <=> %s) as similarity
        FROM multi_vector_embeddings
        WHERE app_id = %s
        ORDER BY similarity DESC
        LIMIT %s
    """, (query_embedding, query.app_id, query.limit))
    
    # 3. Reranking
    reranked = await reranker.rerank(query.text, results)
    
    # 4. Генерация ответа
    response = await llm.generate(
        prompt=query.text,
        context=reranked,
        model=query.model or "gpt-4"
    )
    
    return response
```

---

## 🔌 Порты и Endpoints

### Локальные порты

| Сервис | Порт | URL | Описание |
|--------|------|-----|----------|
| UI | 3000 | http://localhost:3000 | Web интерфейс |
| API | 8000 | http://localhost:8000 | REST API |
| API Docs | 8000 | http://localhost:8000/docs | Swagger UI |
| Redoc | 8000 | http://localhost:8000/redoc | ReDoc |

### Modal.com Endpoints

| Endpoint | URL | Метод | Описание |
|----------|-----|-------|----------|
| Process ColPali | https://rugusev--morphik-processor-process-colpali.modal.run | POST | Обработка изображений |
| Health Check | https://rugusev--morphik-processor-health.modal.run | GET | Проверка статуса |
| App Stats | Modal Dashboard | - | Статистика использования |

### Hetzner Server (135.181.106.12)

| Сервис | Порт | Протокол | Доступ |
|--------|------|----------|--------|
| PostgreSQL | 5432 | TCP | Internal + Modal |
| Redis | 6379 | TCP | Internal only |
| Ollama | 11434 | HTTP | Internal only |
| MinIO | 32000 | HTTP | Internal + External |

---

## 🎯 Зачем нужна эта система

### Проблемы, которые решает Morphik v2.0

1. **Визуальное понимание документов**
   - Традиционные RAG системы теряют 60% информации из PDF (графики, таблицы, диаграммы)
   - ColPali на GPU понимает визуальный контекст без OCR
   - Поиск по смыслу изображений, а не только тексту

2. **Экономия на инфраструктуре**
   - GPU A100 стоит $4/час постоянно vs $0.012/мин на Modal.com
   - Auto-scaling: платим только за реальное использование
   - Экономия до 90% на GPU ресурсах

3. **Enterprise-ready архитектура**
   - Multi-tenancy через app_id
   - JWT аутентификация с user scoping
   - Изоляция данных между приложениями
   - Готовность к масштабированию

4. **Гибридная обработка**
   - Локальные LLM через Ollama для конфиденциальности
   - Cloud модели (GPT-4, Claude) для сложных задач
   - ColPali на Modal.com для визуального анализа
   - Выбор модели под конкретную задачу

### Основные use cases

- **Анализ финансовых отчетов**: Извлечение данных из графиков и таблиц
- **Медицинские документы**: Понимание рентгеновских снимков и диаграмм
- **Техническая документация**: Поиск по схемам и чертежам
- **Научные статьи**: Анализ формул и визуализаций
- **Юридические документы**: Работа со сканами и подписями

---

## 🚀 Git Deployment и CI/CD

### Репозитории и схема деплоя

```
Локальная разработка (/Users/fedor/PycharmProjects/PythonProject/Morphik_local)
    ↓ git push
GitHub (https://github.com/We-are-Humans-Corp/Morphik_local.git)
    ↓ git pull (через SSH)
Production Server (135.181.106.12)
    ↓ docker-compose restart
Live System
```

### Быстрые команды для деплоя

#### 1. Быстрый пуш с автодеплоем
```bash
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_local && \
git add . && \
git commit -m "feat: описание изменений" && \
git push origin main && \
ssh root@135.181.106.12 "cd /opt/morphik && git pull && docker-compose restart"
```

#### 2. Деплой Modal.com функции
```bash
# Локально
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_local
modal deploy morphik_processor_fixed.py

# Проверка
curl https://rugusev--morphik-processor-health.modal.run
```

#### 3. Полный деплой с проверкой
```bash
# Использовать готовый скрипт
./deploy_and_check.sh

# Или вручную
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_local && \
echo "📊 Проверка статуса..." && \
git status --short && \
read -p "➡️ Комментарий коммита: " msg && \
git add . && \
git commit -m "$msg" && \
git push origin main && \
ssh root@135.181.106.12 "cd /opt/morphik && git pull && docker-compose down && docker-compose up -d" && \
echo "✅ Деплой завершен!"
```

### SSH доступ к серверу

```bash
# Прямое подключение
ssh root@135.181.106.12

# Быстрая команда на сервере
ssh root@135.181.106.12 "docker ps"

# Просмотр логов
ssh root@135.181.106.12 "docker logs morphik-api -f"
```

### Правила коммитов

- `feat:` - новая функциональность
- `fix:` - исправление багов
- `docs:` - обновление документации
- `refactor:` - рефакторинг кода
- `test:` - добавление тестов
- `chore:` - обновление зависимостей

---

## 🚀 Запуск системы

### Быстрый старт (все сервисы)

```bash
# 1. Клонирование репозитория
git clone https://github.com/yourusername/morphik.git
cd morphik/modal-morphik_test

# 2. Настройка окружения
cp .env.example .env
# Отредактируйте .env с вашими ключами

# 3. Запуск Docker сервисов
docker-compose down  # Остановка старых контейнеров
docker-compose up -d --build

# 4. Проверка статуса
docker ps
curl http://localhost:8000/health

# 5. Открытие UI
open http://localhost:3000
```

### Запуск отдельных компонентов

```bash
# Только API
docker-compose up morphik -d

# Только UI
docker-compose up ui -d

# Worker (включен в API контейнер)
# Запускается автоматически с API

# Modal.com deployment
modal deploy morphik_processor_fixed.py
```

### Остановка системы

```bash
# Мягкая остановка
docker-compose down

# Полная очистка (включая volumes)
docker-compose down -v

# Остановка Modal
modal app stop morphik-processor
```

---

## ⚙️ Конфигурация

### morphik.toml (основная конфигурация)

```toml
[api]
host = "0.0.0.0"
port = 8000
reload = true

[auth]
jwt_algorithm = "HS256"
dev_mode = true
dev_entity_id = "dev_user"
dev_entity_type = "developer"

[registered_models]
# OpenAI
openai_gpt4 = { model_name = "gpt-4-turbo-preview" }
openai_gpt4_mini = { model_name = "gpt-4-mini" }

# Anthropic
claude_sonnet = { model_name = "claude-3-sonnet-latest" }

# Ollama (local)
ollama_llama = { model_name = "ollama/llama3.2:3b", api_base = "http://135.181.106.12:11434" }

# Embeddings
openai_embedding = { model_name = "text-embedding-3-small" }
colpali_embedding = { model_name = "colpali", api_base = "modal" }

[database]
provider = "postgres"
host = "135.181.106.12"
port = 5432
database = "morphik"
pool_size = 10

[embedding]
model = "colpali_embedding"  # Для изображений
fallback_model = "openai_embedding"  # Для текста

[storage]
provider = "s3"
endpoint_url = "http://135.181.106.12:32000"
bucket = "morphik-storage"
```

### .env (переменные окружения)

```env
# Database
POSTGRES_URI=postgresql+asyncpg://morphik:morphik@135.181.106.12:5432/morphik
REDIS_HOST=135.181.106.12
REDIS_PORT=6379

# Modal.com
MODAL_TOKEN_ID=your_modal_token_id
MODAL_TOKEN_SECRET=your_modal_token_secret
MORPHIK_EMBEDDING_API_DOMAIN=https://rugusev--morphik-processor-process-colpali.modal.run

# Storage
AWS_ACCESS_KEY_ID=uvqsdyUADcc1Uygu298j
AWS_SECRET_ACCESS_KEY=3jwYrh9tIstk9EL8vmLMfnZwRqHdzssGfRR391or
AWS_ENDPOINT_URL=http://135.181.106.12:32000
S3_BUCKET_NAME=morphik-storage

# API Keys (optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  morphik:
    build: .
    container_name: morphik-colpali-configured
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_URI=${POSTGRES_URI}
      - REDIS_HOST=${REDIS_HOST}
      - MODAL_TOKEN_ID=${MODAL_TOKEN_ID}
      - MODAL_TOKEN_SECRET=${MODAL_TOKEN_SECRET}
    volumes:
      - ./morphik.toml:/app/morphik.toml
      - ./storage:/app/storage
    depends_on:
      - postgres-check
    networks:
      - morphik-network

  ui:
    build: ./ee/ui-component
    container_name: morphik-ui-distributed  
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - morphik
    networks:
      - morphik-network

networks:
  morphik-network:
    driver: bridge
```

---

## 🌐 API Документация

### Основные endpoints

#### Аутентификация
```http
POST /auth/register
POST /auth/login
GET /auth/me
POST /auth/refresh
```

#### Документы
```http
POST /v1/ingest/files      # Загрузка документов
GET /v1/documents          # Список документов
GET /v1/documents/{id}     # Детали документа
DELETE /v1/documents/{id}  # Удаление
POST /v1/query            # Поиск по документам
```

#### Чат
```http
POST /v1/chat/completions  # Чат с AI
GET /v1/chats             # История чатов
POST /v1/chats            # Создать чат
GET /v1/chats/{id}        # Получить чат
```

#### Модели
```http
GET /v1/models            # Список моделей
POST /v1/models/config    # Настройка модели
```

#### Графы знаний
```http
POST /v1/graph/extract    # Извлечение сущностей
GET /v1/graph/{doc_id}    # Граф документа
POST /v1/graph/query      # Запрос к графу
```

### Примеры запросов

#### Загрузка документа с ColPali
```bash
curl -X POST http://localhost:8000/v1/ingest/files \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F 'metadata={"use_colpali": true, "app_id": "morphik_app"}'
```

#### Поиск с визуальным контентом
```bash
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "Show me all charts about revenue",
    "use_colpali": true,
    "app_id": "morphik_app",
    "limit": 10
  }'
```

---

## 📊 Мониторинг и диагностика

### Проверка здоровья системы

```bash
# API Health
curl http://localhost:8000/health

# Modal.com status
curl https://rugusev--morphik-processor-health.modal.run

# PostgreSQL
psql -h 135.181.106.12 -U morphik -d morphik -c "SELECT COUNT(*) FROM multi_vector_embeddings;"

# Redis
redis-cli -h 135.181.106.12 ping

# Ollama
curl http://135.181.106.12:11434/api/tags
```

### Просмотр логов

```bash
# API logs
docker logs morphik-colpali-configured -f

# UI logs
docker logs morphik-ui-distributed -f

# Modal logs
modal app logs morphik-processor
```

### Метрики производительности

```sql
-- Статистика embeddings
SELECT 
    document_id,
    COUNT(*) as chunks,
    pg_size_pretty(SUM(LENGTH(content)::bigint)) as total_size,
    MAX(created_at) as last_updated
FROM multi_vector_embeddings
GROUP BY document_id
ORDER BY last_updated DESC;

-- Производительность поиска
EXPLAIN ANALYZE
SELECT document_id, 1 - (embeddings <=> '[...]'::vector) as similarity
FROM multi_vector_embeddings
ORDER BY embeddings <=> '[...]'::vector
LIMIT 10;
```

### Диагностические скрипты

```bash
# Тест подключения к Modal
python test_modal_postgres_connection.py

# Проверка embeddings
python check_postgres_embeddings.py

# Тест ColPali endpoint
python test_colpali_endpoint.py
```

---

## 🔄 Миграция с v1.0

### Основные изменения

1. **ColPali через Modal.com** вместо локального GPU
2. **Base64 изображения** в PostgreSQL вместо S3 путей
3. **Прямая запись** из Modal в PostgreSQL
4. **BFloat16 → Float32** конвертация
5. **JWT с app_id** для multi-tenancy

### Шаги миграции

```bash
# 1. Backup данных
pg_dump -h 135.181.106.12 -U morphik morphik > backup_v1.sql

# 2. Обновление схемы БД
psql -h 135.181.106.12 -U morphik morphik < migrations/v2_schema.sql

# 3. Deploy Modal функции
modal deploy morphik_processor_fixed.py

# 4. Обновление конфигурации
cp morphik.toml.v2 morphik.toml
cp .env.v2 .env

# 5. Пересборка Docker образов
docker-compose build --no-cache

# 6. Запуск новой версии
docker-compose up -d

# 7. Проверка
curl http://localhost:8000/health
python test_modal_postgres_connection.py
```

### Обратная совместимость

- Старые документы без ColPali embeddings продолжают работать
- API endpoints совместимы с v1.0
- Можно переобработать старые документы через ColPali

---

## 🛠️ Troubleshooting

### Частые проблемы и решения

#### ColPali token mismatch error
```
Error: "Got ids=[50] and text=[1024]"
Решение: Установлен max_length=2048, truncation=False
```

#### BFloat16 serialization error
```
Error: "Got unsupported ScalarType BFloat16"
Решение: Добавлена конвертация .to(torch.float32)
```

#### Modal не может записать в PostgreSQL
```
Проверить:
1. Firewall правила на Hetzner
2. PostgreSQL pg_hba.conf разрешает Modal IP
3. Credentials в Modal secrets
```

#### Docker контейнеры не запускаются
```bash
# Проверить логи
docker-compose logs

# Пересборка с нуля
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## 📚 Дополнительные ресурсы

### Документация
- [COLPALI_COMPLETE_SETUP.md](./COLPALI_COMPLETE_SETUP.md) - Детальная настройка ColPali
- [Modal.com Docs](https://modal.com/docs) - Документация Modal
- [ColPali Paper](https://arxiv.org/abs/2407.01449) - Научная статья

### Репозитории
- **GitHub**: https://github.com/yourusername/morphik
- **Modal App**: https://modal.com/apps/morphik-processor
- **Docker Hub**: dockerhub.com/r/morphik/morphik

### Поддержка
- **Issues**: GitHub Issues
- **Email**: support@morphik.ai
- **Discord**: discord.gg/morphik

---

## 📈 Roadmap v3.0

### Q1 2025
- [ ] Streaming responses для больших документов
- [ ] Multi-GPU support в Modal
- [ ] Кеширование embeddings в Redis

### Q2 2025  
- [ ] Kubernetes deployment
- [ ] GraphQL API
- [ ] Mobile applications

### Q3 2025
- [ ] Real-time collaboration
- [ ] Plugin система
- [ ] Self-hosted Modal alternative

---

*Последнее обновление: 11.01.2025 | Версия: 2.0 | Автор: Morphik Team*