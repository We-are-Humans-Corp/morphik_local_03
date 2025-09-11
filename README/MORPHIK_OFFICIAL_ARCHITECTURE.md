# Архитектура и анализ официального Morphik

## Обзор системы

Morphik - это платформа для интеллектуальной обработки документов с использованием RAG (Retrieval-Augmented Generation) и мультимодальных моделей. Система поддерживает как текстовую, так и визуальную обработку документов через интеграцию с ColPali.

## Архитектура системы

### 1. Компоненты системы

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (UI)                       │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                    API Layer (FastAPI)                   │
│  • /ingest/file - загрузка документов                   │
│  • /query - поиск по документам                         │
│  • /documents - управление документами                   │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┬─────────────┐
        │                         │             │
┌───────▼──────┐  ┌──────────────▼──┐  ┌───────▼────────┐
│ Redis Queue  │  │  Object Storage │  │  PostgreSQL    │
│              │  │  (MinIO/S3)     │  │  + pgvector    │
└───────┬──────┘  └─────────────────┘  └────────────────┘
        │
┌───────▼─────────────────────────────────────────────────┐
│            Ingestion Worker (Background)                 │
│  • Парсинг документов                                   │
│  • Создание чанков                                      │
│  • Генерация эмбеддингов                                │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴───────────────┐
        │                              │
┌───────▼──────┐            ┌─────────▼────────┐
│   ColPali    │            │  Text Embedding  │
│   (Modal)    │            │     Models       │
└──────────────┘            └──────────────────┘
```

## Процесс обработки документов

### 1. Загрузка документа

**Endpoint:** `POST /ingest/file`

```python
# 1. Файл загружается через API
# 2. Создается Document в БД со статусом "processing"
# 3. Файл сохраняется в Object Storage (MinIO/S3)
# 4. Создается задача для воркера в Redis Queue

{
    "document_id": "uuid",
    "status": "processing",
    "storage_info": {
        "bucket": "morphik-storage",
        "key": "ingest_uploads/{uuid}/filename.pdf"
    }
}
```

### 2. Асинхронная обработка (Ingestion Worker)

#### 2.1 Определение типа файла и стратегии обработки

```python
# Проверка условий для ColPali
is_colpali_native_format = mime_type in [
    "application/pdf",
    "image/png", 
    "image/jpeg",
    "application/vnd.openxmlformats-officedocument.*"
]

using_colpali = (
    use_colpali and 
    settings.ENABLE_COLPALI and
    document_service.colpali_embedding_model and 
    document_service.colpali_vector_store
)
```

#### 2.2 Обработка PDF документов

**Текстовая обработка (если ColPali выключен):**
```python
# Используется unstructured библиотека
text = parse_document(pdf_content)
chunks = split_text(text, chunk_size=1000, overlap=200)
embeddings = text_embedding_model.embed(chunks)
```

**Визуальная обработка (если ColPali включен):**
```python
# В методе _create_chunks_multivector:
case "application/pdf":
    # 1. Конвертация страниц в изображения
    if use_pymupdf:
        images = convert_pdf_pages_pymupdf(pdf_content, dpi=150)
    else:
        images = pdf2image.convert_from_bytes(pdf_content)
    
    # 2. Обработка изображений
    for page_num, image in enumerate(images):
        # Сжатие изображения
        image = resize_image(image, max_width=256)
        image_b64 = convert_to_jpeg(image, quality=70)
        
        # Создание чанка для страницы
        chunk = Chunk(
            content=image_b64,
            metadata={"is_image": True}
            # Важно: номер страницы НЕ сохраняется в метаданных!
            # Страница определяется по chunk_number
        )
```

### 3. ColPali интеграция

#### 3.1 Режимы работы ColPali

```python
# config.py
COLPALI_MODE: Literal["off", "local", "api"] = "local"
ENABLE_COLPALI: bool = True
```

- **"off"** - ColPali выключен
- **"local"** - Локальная модель ColPali
- **"api"** - Внешний API (HuggingFace, Modal, RunPod)

#### 3.2 API режим (используется для Modal)

```python
class ColpaliApiEmbeddingModel:
    async def embed_for_ingestion(self, chunks):
        # 1. Разделение на текст и изображения
        text_inputs, image_inputs = partition_chunks(chunks)
        
        # 2. Отправка на API
        payload = {
            "input_type": "image",
            "inputs": image_inputs  # base64 изображения
        }
        
        # 3. Получение ответа
        if "modal.run" in endpoint:
            # Modal возвращает .npz файл
            npz_data = np.load(response.content)
            embeddings = extract_embeddings(npz_data)
        else:
            # JSON ответ
            embeddings = response.json()["embeddings"]
        
        return embeddings  # MultiVector формат
```

### 4. Хранение данных

#### 4.1 Структура хранения

```
Object Storage (MinIO/S3):
├── ingest_uploads/          # Оригинальные файлы
│   └── {uuid}/
│       └── document.pdf
└── multivector-chunks/      # НЕ используется для изображений!
    └── (только для текстовых чанков)

PostgreSQL + pgvector:
├── documents               # Метаданные документов
├── document_chunks         # Чанки и их эмбеддинги
└── folders                # Организация документов
```

#### 4.2 Векторные хранилища

- **Основное хранилище** - для текстовых эмбеддингов
- **ColPali хранилище** - для мультивекторных эмбеддингов изображений

### 5. Поиск и вывод

#### 5.1 Процесс поиска

```python
# 1. Получение запроса
query = "Найти информацию о..."

# 2. Параллельный поиск
results = await gather(
    text_vector_store.search(query, k=20),
    colpali_vector_store.search(query, k=20) if use_colpali
)

# 3. Объединение и ранжирование
combined_results = combine_and_rerank(results)
```

#### 5.2 Формат ссылок на источники

```python
# В litellm_completion.py
def format_citations(chunk, metadata):
    if is_colpali_chunk:
        # Определение страницы по chunk_number
        page_num = chunk.chunk_number + 1
        return f"[{filename}, page {page_num}]"
    else:
        return f"[{filename}]"

# Пример вывода:
"Екатерина училась в МГУ [CV_Ekaterina_Nobs.pdf, page 2]"
```

## Ключевые особенности

## Критические детали реализации

### 1. Номера страниц PDF
**ВАЖНО:** В официальном Morphik номер страницы PDF **НЕ сохраняется** в метаданных чанка. Вместо этого используется `chunk_number`:
- Страница 1 = chunk_number 0
- Страница 2 = chunk_number 1
- И так далее

### 2. Сжатие изображений и оптимизация
Все изображения страниц сжимаются:
- Максимальная ширина: 256px
- JPEG качество: 70%
- DPI для рендеринга: 150 (настраивается через COLPALI_PDF_DPI)
- Memory footprint: ~256 KB на страницу для multi-vector embeddings

**Продвинутая оптимизация PyMuPDF:**
```python
doc.scrub(metadata=True, thumbnails=True)  # Удаление метаданных
doc.rewrite_images(dpi_target=72, quality=60)  # Сжатие изображений  
doc.ez_save("optimized.pdf")  # Авто-оптимизация
```

### 3. Modal интеграция
При использовании Modal:
- Endpoint должен быть настроен на modal.run
- Ответ приходит в формате .npz, а не JSON
- API key не требуется для публичных endpoints

### 4. Хранение чанков
- Текстовые чанки могут храниться в multivector-chunks/
- Изображения страниц PDF хранятся только как эмбеддинги
- Оригинальный PDF всегда сохраняется целиком

## Отличия от вашей текущей реализации

| Аспект | Официальный Morphik | Ваша система |
|--------|-------------------|--------------|
| PDF обработка | PyMuPDF → сжатые изображения | pdf2image → полные изображения |
| Номер страницы | Через chunk_number | Добавлен в metadata |
| Ссылки | На PDF страницы | На текстовые чанки |
| ColPali режим | local/api конфигурация | Только Modal API |
| Хранение | PDF целиком + эмбеддинги | PDF + текстовые чанки |

## Рекомендации по исправлению

1. **Убрать сохранение текстовых чанков** для PDF при использовании ColPali
2. **Использовать chunk_number** для определения страницы вместо metadata
3. **Настроить правильный COLPALI_MODE** = "api" в конфигурации
4. **Добавить сжатие изображений** для оптимизации
5. **Исправить формат ссылок** на `[filename, page X]`

## Дополнительные технические детали

### ColPali оптимизации
- **Memory footprint:** 256 KB на страницу для multi-vector embeddings
- **Batch processing:** 4 страницы одновременно для оптимального использования GPU
- **DPI настройка:** Переменная COLPALI_PDF_DPI (default: 150)

### Производительность системы
- **Query latency:** ColPali ~30ms vs традиционные модели ~22ms
- **Indexing speed:** Ускорение за счет отсутствия OCR preprocessing
- **Late interaction overhead:** ~1ms на 1000 страниц документов
- **Оптимальный батч:** 4 страницы для GPU памяти

### PyMuPDF продвинутые возможности
```python
# Дополнительная оптимизация PDF
doc.scrub(metadata=True, thumbnails=True)  # Удаление метаданных
doc.rewrite_images(dpi_target=72, quality=60)  # Пересжатие изображений
doc.ez_save("optimized.pdf")  # Автоматическая оптимизация
```

---

*Документ создан на основе анализа официального репозитория [morphik-org/morphik-core](https://github.com/morphik-org/morphik-core)*

