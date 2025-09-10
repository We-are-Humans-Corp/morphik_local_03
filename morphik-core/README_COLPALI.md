# Morphik + ColPali + Modal Integration

Полная настройка Morphik Core с ColPali через Modal API.

## 🚀 Быстрый старт

1. **Настройте переменные окружения в .env:**
   ```bash
   # Добавьте ваши API ключи:
   OPENAI_API_KEY="sk-..."
   MORPHIK_EMBEDDING_API_KEY="your-modal-key"
   MORPHIK_EMBEDDING_API_DOMAIN="https://your-username--morphik-colpali-serve.modal.run"
   ```

2. **Запустите систему:**
   ```bash
   ./start_morphik_colpali.sh
   ```

3. **Деплойте Modal API:**
   ```bash
   # Установите modal
   pip install modal
   
   # Авторизуйтесь
   modal auth new
   
   # Деплойте API
   modal deploy modal_colpali_api.py
   
   # Получите URL и обновите .env
   ```

4. **Запустите тесты:**
   ```bash
   python test_colpali_integration.py
   ```

## 📊 Мониторинг

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

## 🔧 Отладка

```bash
# Логи Morphik
docker-compose -f docker-compose.dev.yml logs -f morphik

# Логи Worker
docker-compose -f docker-compose.dev.yml logs -f worker

# Логи PostgreSQL
docker-compose -f docker-compose.dev.yml logs -f postgres

# Modal логи
modal logs morphik-colpali
```

## 🛠️ Архитектура

- **Morphik Core** (Docker) - основная система с PostgreSQL + pgvector
- **Modal ColPali API** - GPU обработка embeddings
- **Правильная интеграция** через .npz формат

## 🎯 Ключевые настройки

- `multivector_store.provider = "postgres"`
- `colpali_mode = "api"`
- `morphik_embedding_api_domain` - ваш Modal URL
- Modal API возвращает .npz формат
- ColQwen2.5 БЕЗ max_length параметров
