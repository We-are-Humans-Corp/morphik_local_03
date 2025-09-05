# MORPHIK SYSTEM ANALYTICS - ПОЛНАЯ АРХИТЕКТУРА И ПРОЦЕСС ОБРАБОТКИ ДОКУМЕНТОВ

## 📊 ОБЩАЯ АРХИТЕКТУРА СИСТЕМЫ

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                             ЛОКАЛЬНАЯ МАШИНА (Docker)                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐        │
│  │   UI (Next.js)  │────▶│   API (FastAPI)  │────▶│  Worker (Arq)   │        │
│  │   Port: 3000    │     │   Port: 8000     │     │   Background     │        │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘        │
│           │                        │                        │                 │
│           │                        │                        │                 │
└───────────│────────────────────────│────────────────────────│─────────────────┘
            │                        │                        │
            │                        ▼                        ▼
            │         ┌──────────────────────────────────────────────────┐
            │         │      ВНЕШНИЙ СЕРВЕР (135.181.106.12)             │
            │         ├──────────────────────────────────────────────────┤
            │         │                                                   │
            │         │  ┌──────────────┐    ┌──────────────┐           │
            │         │  │  PostgreSQL  │    │    Redis     │           │
            │         │  │  + pgvector  │    │  Port: 6379  │           │
            │         │  │  Port: 5432  │    │              │           │
            │         │  └──────────────┘    └──────────────┘           │
            │         │                                                   │
            │         │  ┌──────────────┐    ┌──────────────┐           │
            │         │  │    MinIO     │    │   Ollama     │           │
            │         │  │ Port: 32000  │    │ Port: 11434  │           │
            │         │  │ S3 Storage   │    │ LLM: llama3.2│           │
            │         │  └──────────────┘    └──────────────┘           │
            │         │                                                   │
            │         └──────────────────────────────────────────────────┘
            │
            │         ┌──────────────────────────────────────────────────┐
            └────────▶│            MODAL.COM (Serverless)                 │
                      ├──────────────────────────────────────────────────┤
                      │                                                   │
                      │         ┌───────────────────────┐                │
                      │         │    ColPali API        │                │
                      │         │  (GPU Processing)     │                │
                      │         │  Model: ColQwen2.5    │                │
                      │         │  Endpoint: HTTPS      │                │
                      │         └───────────────────────┘                │
                      │                                                   │
                      └──────────────────────────────────────────────────┘
```

## 🔄 ДЕТАЛЬНЫЙ ПРОЦЕСС ЗАГРУЗКИ И ОБРАБОТКИ ДОКУМЕНТА

### ЭТАП 1: UI - ЗАГРУЗКА ФАЙЛА
**Расположение**: `ee/ui-component/` (Next.js, порт 3000)

```javascript
// UI отправляет файл через multipart/form-data
POST http://localhost:8000/ingest/files
Headers:
  - Authorization: Bearer {JWT_TOKEN}
  - Content-Type: multipart/form-data
Body:
  - files: [PDF файл]
  - metadata: "{}"
  - rules: "[]"
  - use_colpali: undefined  // ⚠️ UI НЕ ПЕРЕДАЕТ ЭТОТ ПАРАМЕТР!
  - folder_name: "1"
```

### ЭТАП 2: API - ПРИЕМ И ВАЛИДАЦИЯ
**Файл**: `/core/routes/ingest.py` (строки 266-439)
**Функция**: `batch_ingest_files()`

#### 2.1 Что мы добавили:
```python
# Строка 305-310:
def str2bool(v):
    if v is None:
        return None
    return v if isinstance(v, bool) else str(v).lower() in {"true", "1", "yes"}

use_colpali_bool = str2bool(use_colpali)
logger.info(f"[BATCH] Initial use_colpali: {use_colpali}, converted to: {use_colpali_bool}")
logger.info(f"[BATCH] ENABLE_COLPALI setting: {settings.ENABLE_COLPALI}")

# Строки 355-360: Автовключение ColPali для PDF
file_use_colpali = use_colpali_bool
if file_use_colpali is None and settings.ENABLE_COLPALI:
    if file.filename and file.filename.lower().endswith('.pdf'):
        file_use_colpali = True
        logger.info(f"Auto-enabled ColPali for PDF file: {file.filename}")
```

#### 2.2 Проблема:
⚠️ **ЛОГИ [BATCH] НЕ ПОЯВЛЯЮТСЯ!** - Это значит код не обновился в Docker образе

#### 2.3 Что происходит дальше:
1. Создается Document stub со статусом "processing"
2. Файл загружается в MinIO (S3): `bucket: morphik-storage`
3. Создается задача в Redis для Worker

```python
# Строки 418-431: Создание задачи
job = await redis.enqueue_job(
    "process_ingestion_job",
    document_id=doc.external_id,
    file_key=stored_key,
    bucket=bucket,
    original_filename=file.filename,
    content_type=file.content_type,
    metadata_json=metadata_json,
    auth_dict=auth_dict,
    rules_list=file_rules,
    use_colpali=file_use_colpali,  # ⚠️ Должно быть True для PDF, но сейчас None
    folder_name=folder_name,
    end_user_id=end_user_id,
)
```

### ЭТАП 3: WORKER - ОБРАБОТКА ДОКУМЕНТА
**Файл**: `/core/workers/ingestion_worker.py`
**Функция**: `process_ingestion_job()`

#### 3.1 Получение задачи из Redis:
```python
async def process_ingestion_job(
    document_id: str,
    file_key: str,
    bucket: str,
    original_filename: str,
    content_type: str,
    metadata_json: str,
    auth_dict: dict,
    rules_list: list = None,
    use_colpali: bool = False,  # ⚠️ Получает None, превращается в False!
    folder_name: str = None,
    end_user_id: str = None,
):
```

#### 3.2 Скачивание файла из MinIO:
```python
# Worker скачивает файл из S3
file_content = await storage.download(file_key, bucket=bucket)
```

#### 3.3 Парсинг документа:
```python
# Если use_colpali=False, используется обычный парсинг
if content_type == "application/pdf" and not use_colpali:
    # Обычная обработка текста из PDF
    chunks = await parser.parse_pdf(file_content)
```

### ЭТАП 4: COLPALI ОБРАБОТКА (НЕ РАБОТАЕТ!)
**Файл**: `/core/embedding/colpali_api_embedding_model.py`

#### Что должно происходить при use_colpali=True:

```python
if use_colpali:
    # 1. Конвертация PDF в изображения
    images = pdf_to_images(file_content)
    
    # 2. Отправка на Modal.com API
    response = await httpx.post(
        "https://rugusev--colpali-morphik-official-fastapi-app.modal.run/embed",
        json={"images": images}
    )
    
    # 3. Получение multi-vector embeddings
    embeddings = response.json()["embeddings"]
    
    # 4. Сохранение в специальную таблицу multi_vectors
    await multi_vector_store.store(embeddings)
```

**⚠️ НО ЭТОГО НЕ ПРОИСХОДИТ, потому что use_colpali=False!**

### ЭТАП 5: СОХРАНЕНИЕ В БАЗУ ДАННЫХ

#### 5.1 PostgreSQL (135.181.106.12:5432):
- **Таблица `documents`**: метаданные документа
- **Таблица `vector_embeddings`**: обычные текстовые эмбеддинги (если не ColPali)
- **Таблица `multi_vectors`**: ColPali эмбеддинги (НЕ СОЗДАЕТСЯ!)

#### 5.2 MinIO (135.181.106.12:32000):
- Оригинальный файл: `morphik-storage/ingest_uploads/{uuid}/{filename}`
- Обработанные чанки: `morphik-storage/chunks/{doc_id}/`

## 🔍 ТЕКУЩИЕ ПРОБЛЕМЫ

### ПРОБЛЕМА 1: Код не обновляется в Docker
```bash
# Мы изменили файл:
/Users/fedor/PycharmProjects/PythonProject/Morphik_local/Test/Morphik_local/core/routes/ingest.py

# Но в Docker контейнере старая версия без логов [BATCH]
docker exec morphik_v2 grep "\[BATCH\]" /app/core/routes/ingest.py
# Результат: пусто
```

### ПРОБЛЕМА 2: UI не передает use_colpali
```javascript
// ee/ui-component/src/services/api.js
// UI всегда отправляет use_colpali=undefined
const formData = new FormData();
formData.append('file', file);
formData.append('metadata', '{}');
// use_colpali НЕ ДОБАВЛЯЕТСЯ!
```

### ПРОБЛЕМА 3: Автовключение не срабатывает
```python
# Должно работать:
if use_colpali_bool is None and settings.ENABLE_COLPALI:
    if file.filename.lower().endswith('.pdf'):
        use_colpali_bool = True  # ✅ Должно включиться
        
# Но не работает потому что:
1. Код не обновлен в Docker образе
2. Логи [BATCH] не появляются
```

## 📋 НАСТРОЙКИ СИСТЕМЫ

### morphik.toml (строки 122-128):
```toml
[morphik]
enable_colpali = true  # ✅ Включено
mode = "self_hosted"
morphik_embedding_api_domain = "https://rugusev--colpali-morphik-official-fastapi-app.modal.run"
colpali_mode = "api"  # Используем Modal API, не локально
```

### docker-compose.v2.yml:
```yaml
services:
  morphik:
    environment:
      - POSTGRES_URI=postgresql+asyncpg://morphik:morphik@135.181.106.12:5432/morphik
      - REDIS_HOST=135.181.106.12
      - OLLAMA_BASE_URL=http://135.181.106.12:11434
      - S3_ENDPOINT_URL=http://135.181.106.12:32000
    # НЕТ volume mapping для /app/core - код запечен в образе!
```

## 🛠 ЧТО НУЖНО ИСПРАВИТЬ

### 1. Пересобрать Docker образ правильно:
```bash
# Убедиться что изменения в файле
docker-compose -f docker-compose.v2.yml build --no-cache morphik worker

# Перезапустить
docker-compose -f docker-compose.v2.yml up -d morphik worker
```

### 2. Проверить что код обновился:
```bash
# Должны увидеть логи [BATCH]
docker exec morphik_v2 grep "\[BATCH\]" /app/core/routes/ingest.py
```

### 3. Загрузить PDF и проверить логи:
```bash
# Должны увидеть:
# [BATCH] Initial use_colpali: None, converted to: None
# [BATCH] ENABLE_COLPALI setting: True
# Auto-enabled ColPali for PDF file: document.pdf
```

### 4. Проверить в базе данных:
```sql
-- Проверить что using_colpali=true
SELECT doc_metadata->>'using_colpali' 
FROM documents 
WHERE external_id = 'xxx';

-- Проверить multi-vectors
SELECT COUNT(*) 
FROM multi_vectors 
WHERE document_id = 'xxx';
```

## 📊 МОНИТОРИНГ И ЛОГИ

### Просмотр логов API:
```bash
docker logs morphik_v2 -f | grep -E "(colpali|ColPali|BATCH|Auto-enabled)"
```

### Просмотр логов Worker:
```bash
docker logs worker_v2 -f | grep -E "(colpali|use_colpali|multi-vector)"
```

### Проверка Modal.com API:
```bash
curl https://rugusev--colpali-morphik-official-fastapi-app.modal.run/health
# Должен вернуть: {"status": "healthy", "service": "colpali"}
```

## 🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

При правильной работе системы:
1. PDF файл автоматически определяется
2. Включается ColPali обработка
3. Файл конвертируется в изображения
4. Изображения отправляются на Modal.com
5. Получаются multi-vector embeddings
6. Сохраняются в специальную таблицу
7. Поиск работает по визуальному содержимому

## ⚠️ КРИТИЧЕСКИЕ ТОЧКИ ОТКАЗА

1. **Docker образ не обновляется** - изменения кода не применяются
2. **UI не передает параметры** - use_colpali всегда undefined
3. **Worker не получает правильные параметры** - use_colpali превращается в False
4. **Modal.com API недоступен** - ColPali не может обработать
5. **База данных не содержит нужных таблиц** - multi_vectors не создана

---
Документ создан: 2025-09-05
Версия системы: Morphik v2
Автор анализа: Claude