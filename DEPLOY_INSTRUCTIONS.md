# 🚀 ИНСТРУКЦИИ ПО ДЕПЛОЮ MORPHIK + COLPALI

## ✅ КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ

### 1️⃣ Деплой исправленного Modal API (NPZ формат)
```bash
# Перейти в папку проекта
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_local/modal-morphik_test/

# Деплоить исправленный API
modal deploy modal_colpali_fixed.py

# Вы получите URL вида:
# https://your-username--morphik-processor-process-colpali.modal.run
```

### 2️⃣ Обновить URL в конфигурации

После деплоя обновите URL в двух местах:

#### .env
```bash
MORPHIK_EMBEDDING_API_DOMAIN="https://your-new-url--morphik-processor-process-colpali.modal.run"
```

#### morphik.toml
```toml
[morphik]
morphik_embedding_api_domain = "https://your-new-url--morphik-processor-process-colpali.modal.run"
```

### 3️⃣ Добавить OpenAI ключ

В файле `.env` замените:
```bash
OPENAI_API_KEY="sk-proj-your-real-openai-key-here"
```

## 📋 ПРОВЕРОЧНЫЙ СПИСОК

✅ **Modal API исправлен:**
- Использует NPZ формат (не JSON)
- БЕЗ max_length параметров
- Resize изображений при необходимости

✅ **Конфигурация правильная:**
- `colpali_mode = "api"`
- `multivector_store.provider = "postgres"`
- Modal URL обновлен после деплоя

✅ **Переменные окружения:**
- AWS_ACCESS_KEY_ID (для S3)
- OPENAI_API_KEY (для embeddings)
- Все Hetzner настройки (PostgreSQL, Redis, MinIO)

## 🔧 ЗАПУСК СИСТЕМЫ

### Вариант 1: Docker Compose
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

## 🧪 ТЕСТИРОВАНИЕ

### 1. Проверить Modal API
```bash
# Health check
curl https://your-url--morphik-processor-process-colpali.modal.run/health

# Должен вернуть:
# {"status": "healthy", "device": "cuda"}
```

### 2. Проверить Morphik API
```bash
# Health check
curl http://localhost:8000/health

# API документация
open http://localhost:8000/docs
```

### 3. Запустить интеграционные тесты
```bash
python test_colpali_integration.py
```

### 4. Проверить сохранение в БД
```bash
# Подключиться к PostgreSQL
psql -h 135.181.106.12 -U morphik -d morphik

# Проверить таблицу
SELECT COUNT(*) FROM multi_vector_embeddings;
```

## 🔍 МОНИТОРИНГ

### Docker логи
```bash
# API логи
docker-compose logs -f morphik

# Worker логи
docker-compose logs -f worker

# PostgreSQL логи
docker-compose logs -f postgres
```

### Modal логи
```bash
modal logs morphik-processor
```

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **NPZ формат критичен!** 
   - Modal API должен возвращать `application/octet-stream`
   - НЕ `application/json`

2. **OpenAI ключ обязателен**
   - Используется для обычных embeddings
   - Модель: text-embedding-3-small

3. **После каждого редеплоя Modal**
   - Обновляйте URL в .env
   - Обновляйте URL в morphik.toml

4. **База данных на Hetzner**
   - PostgreSQL: 135.181.106.12:5432
   - Redis: 135.181.106.12:6379
   - MinIO S3: 135.181.106.12:32000

## 📊 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После правильной настройки:
1. ✅ Modal API возвращает NPZ формат
2. ✅ ColPali обрабатывает изображения без ошибок токенизации
3. ✅ Embeddings сохраняются в PostgreSQL
4. ✅ Поиск по ColPali работает корректно

## 🆘 TROUBLESHOOTING

### Ошибка "Mismatch in token count"
- Проверьте, что используется `modal_colpali_fixed.py`
- Убедитесь, что НЕТ параметров max_length

### Ошибка "No embeddings returned"
- Проверьте NPZ формат в Modal API
- Проверьте логи: `modal logs morphik-processor`

### Embeddings не сохраняются в БД
- Проверьте MULTIVECTOR_STORE_PROVIDER=postgres
- Проверьте подключение к Hetzner PostgreSQL

### Ошибка OpenAI API
- Добавьте реальный OPENAI_API_KEY в .env