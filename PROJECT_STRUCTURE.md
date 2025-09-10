# 📁 СТРУКТУРА ПРОЕКТА MORPHIK + COLPALI + MODAL

## 🎯 Текущее расположение
```
/Users/fedor/PycharmProjects/PythonProject/Morphik_local/modal-morphik_test/
```

## 📂 Структура папок и файлов

### 🔧 Конфигурационные файлы (корень проекта)
```
modal-morphik_test/
├── 📄 .env                           # ✅ Настроен для Hetzner + Modal
├── 📄 morphik.toml                   # ✅ colpali_mode = "api", правильный Modal URL
├── 📄 docker-compose.yml              # Основной Docker compose
├── 📄 docker-compose.dev.yml          # Development Docker compose
└── 📄 dockerfile                      # Основной Dockerfile с ColPali
```

### 🐍 Python скрипты для тестирования
```
modal-morphik_test/
├── 📄 modal_colpali_fixed.py        # ✅ ИСПРАВЛЕННЫЙ Modal API с NPZ форматом
├── 📄 modal_colpali_api.py          # Старый Modal API (JSON формат)
├── 📄 test_colpali_integration.py   # Тесты интеграции
├── 📄 apply_debug_patches.py        # ✅ Debug патчи применены
└── 📄 setup_morphik_colpali.py      # Скрипт автоматической настройки
```

### 📝 Документация
```
modal-morphik_test/
├── 📄 DEPLOY_INSTRUCTIONS.md         # ✅ Инструкции по деплою с исправлениями
├── 📄 PROJECT_STRUCTURE.md           # Этот файл - структура проекта
└── 📄 README_COLPALI.md              # Документация ColPali интеграции
```

### 📦 Основной код Morphik
```
modal-morphik_test/
├── core/                             # Основной код Morphik
│   ├── embedding/
│   │   ├── colpali_embedding_model.py       # Локальная модель ColPali
│   │   └── colpali_api_embedding_model.py   # ✅ API клиент с debug логами
│   ├── api.py                        # FastAPI приложение
│   ├── config.py                     # Конфигурация
│   ├── services_init.py              # Инициализация сервисов
│   └── ... (остальные модули)
├── ee/                               # Enterprise Edition
│   └── ui-component/                 # Frontend (Next.js)
└── sdks/                             # SDK для Python
```

### 📁 Вложенная папка morphik-core (от скрипта)
```
modal-morphik_test/
└── morphik-core/                     # Созданная скриптом папка
    ├── .env                          # Дубликат конфигурации
    ├── morphik.toml                  # Дубликат конфигурации
    ├── docker-compose.dev.yml        # Docker для разработки
    ├── modal_colpali_api.py          # Modal API код
    ├── test_colpali_integration.py   # Тесты
    ├── apply_debug_patches.py        # Debug патчи
    ├── start_morphik_colpali.sh      # Скрипт запуска
    └── README_COLPALI.md             # Документация
```

## ⚙️ Ключевые настройки

### 📄 .env файл
```bash
# PostgreSQL (Hetzner - 135.181.106.12)
POSTGRES_URI="postgresql+asyncpg://morphik:morphik@135.181.106.12:5432/morphik"

# Redis (Hetzner)
REDIS_HOST=135.181.106.12
REDIS_PORT=6379

# MinIO S3 (Hetzner)
S3_ENDPOINT_URL=http://135.181.106.12:32000
S3_ACCESS_KEY_ID=uvqsdyUADcc1Uygu298j
S3_SECRET_ACCESS_KEY=3jwYrh9tIstk9EL8vmLMfnZwRqHdzssGfRR391or

# Modal ColPali API
MORPHIK_EMBEDDING_API_DOMAIN="https://rugusev--morphik-processor-process-colpali.modal.run"
MORPHIK_EMBEDDING_API_KEY="dummy_key_for_modal"

# ⚠️ НУЖНО ДОБАВИТЬ:
OPENAI_API_KEY=""  # Для обычных embeddings
```

### 📄 morphik.toml
```toml
[morphik]
enable_colpali = true
colpali_mode = "api"  # Используем Modal API
morphik_embedding_api_domain = "https://rugusev--morphik-processor-process-colpali.modal.run"

[multivector_store]
provider = "postgres"  # НЕ "morphik"!

[database]
provider = "postgres"
pool_size = 10

[embedding]
model = "openai_embedding"  # Требует OPENAI_API_KEY
```

## ✅ Что уже сделано

1. **Конфигурация подключения к Hetzner**
   - PostgreSQL на 135.181.106.12
   - Redis на 135.181.106.12
   - MinIO S3 на 135.181.106.12:32000

2. **Интеграция с Modal ColPali**
   - URL: https://rugusev--morphik-processor-process-colpali.modal.run
   - Режим: colpali_mode = "api"
   - ✅ **СОЗДАН ИСПРАВЛЕННЫЙ modal_colpali_fixed.py с NPZ форматом**

3. **Debug патчи применены**
   - Добавлено логирование в colpali_api_embedding_model.py
   - Логи покажут запросы к Modal API

4. **Исправления в modal_colpali_fixed.py**
   - ✅ Убраны параметры max_length (вызывали ошибку токенизации)
   - ✅ Возвращает NPZ формат вместо JSON
   - ✅ media_type="application/octet-stream"
   - ✅ Добавлен resize изображений при необходимости

## ⚠️ Что нужно сделать программисту

1. **Деплой исправленного Modal API**
   ```bash
   # Нужно добавить git в образ и исправить устаревшие параметры
   modal deploy modal_colpali_fixed.py
   ```
   - После деплоя получить новый URL
   - Обновить URL в .env и morphik.toml

2. **Добавить OPENAI_API_KEY в .env**
   - Требуется для обычных embeddings
   - Модель: text-embedding-3-small
   - Заменить "sk-proj-your-openai-key-here" на реальный ключ

3. **Протестировать интеграцию**
   - Запустить тесты: `python test_colpali_integration.py`
   - Проверить сохранение embeddings в PostgreSQL

## 🚀 Как запустить

### Вариант 1: Docker (рекомендуется)
```bash
cd modal-morphik_test
docker-compose up --build
```

### Вариант 2: Локально
```bash
cd modal-morphik_test
pip install -r requirements.txt
python start_server.py
```

### Вариант 3: Использовать скрипт из morphik-core
```bash
cd modal-morphik_test/morphik-core
./start_morphik_colpali.sh
```

## 📊 Тестирование

```bash
# Запустить тесты интеграции
python test_colpali_integration.py

# Проверить health API
curl http://localhost:8000/health

# Проверить Modal endpoint
curl https://rugusev--morphik-processor-process-colpali.modal.run/health
```

## 🔍 Мониторинг

- **API документация**: http://localhost:8000/docs
- **Логи Docker**: `docker-compose logs -f morphik`
- **Логи Worker**: `docker-compose logs -f worker`
- **PostgreSQL проверка**: 
  ```sql
  SELECT COUNT(*) FROM multi_vector_embeddings;
  ```

## 📝 Примечания для программиста

1. **РЕШЕНА проблема форматов**:
   - ✅ Создан modal_colpali_fixed.py с NPZ форматом
   - ✅ Убраны параметры max_length (вызывали ошибку)
   - ⚠️ Нужно задеплоить исправленный файл

2. **Структура проекта дублирована**:
   - Основные файлы в корне modal-morphik_test
   - Дубликаты в morphik-core/ (созданы скриптом)
   - Рекомендую использовать корневые файлы

3. **БД на Hetzner работает**, но embeddings не сохраняются:
   - Проверить передачу document_id и chunk_id
   - Проверить логи после загрузки документов

4. **Modal endpoint текущий статус**:
   - URL: https://rugusev--morphik-processor-process-colpali.modal.run
   - Возвращает ошибку токенизации
   - ⚠️ **НУЖЕН РЕДЕПЛОЙ с modal_colpali_fixed.py**

## 🔴 КРИТИЧЕСКИЕ ИЗМЕНЕНИЯ В modal_colpali_fixed.py

1. **Исправление установки зависимостей**:
   ```python
   # Нужно добавить git в образ:
   .apt_install(["git"])
   ```

2. **Обновление устаревших параметров Modal**:
   ```python
   # Было: gpu=modal.gpu.A100(count=1, size="40GB")
   # Нужно: gpu="A100-40GB"
   
   # Было: container_idle_timeout=300
   # Нужно: scaledown_window=300
   
   # Было: allow_concurrent_inputs=10
   # Нужно: использовать декоратор @modal.concurrent
   ```