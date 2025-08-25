# Morphik - Текущая Архитектура Системы

## 📋 Оглавление
- [Обзор](#обзор)
- [Архитектура](#архитектура)
- [Компоненты](#компоненты)
- [Конфигурация](#конфигурация)
- [Запуск системы](#запуск-системы)
- [Docker образы](#docker-образы)
- [Решение проблем](#решение-проблем)

## 🎯 Обзор

Morphik - это распределенная система обработки документов и работы с LLM моделями, использующая гибридную архитектуру с локальными и удаленными компонентами.

### Текущее состояние (25.08.2025)
- **API и Worker**: Запускаются локально в Docker
- **UI**: Запускается локально через npm для разработки  
- **Тяжелые сервисы**: Вынесены на удаленный сервер 135.181.106.12
- **ColPali GPU сервис**: Serverless на RunPod для обработки изображений в PDF
- **Фильтрация моделей**: Показываются только доступные модели на основе API ключей
- **Аутентификация**: Исправлена, использует SHA256 с солью
- **Unified User System**: Система работает с единым пользователем demotest (ID: 8)

## 🏗️ Архитектура

### Схема взаимодействия компонентов

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   Local API     │    │  RunPod Server  │
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
| UI | Локально (npm dev) | 3000 | Next.js интерфейс для разработки |
| API | Локально (Docker) | 8000 | FastAPI сервер |
| Worker | Локально (Docker) | - | Arq worker для фоновых задач |
| PostgreSQL | Hetzner сервер | 5432 | База данных с pgvector |
| Redis | Hetzner сервер | 6379 | Кеш и очереди задач |
| Ollama | Hetzner сервер | 11434 | LLM модели (llama3.2:3b) |
| MinIO | Hetzner сервер | 9000 | Объектное хранилище |
| ColPali | RunPod GPU | HTTPS | Обработка изображений в PDF (serverless) |

## 🔧 Компоненты

### API (morphik_local-morphik)
- **Образ**: 3GB
- **Технологии**: FastAPI, Python 3.11, UV
- **Функции**:
  - REST API endpoints
  - Аутентификация JWT
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
- **Образ**: 201MB (для production)
- **Технологии**: Next.js 14, React, TypeScript
- **Функции**:
  - Чат интерфейс
  - Управление документами
  - Визуализация графов
  - PDF viewer

### ColPali (RunPod GPU)
- **Расположение**: RunPod serverless (fl73vpjsrfqhmn)
- **Технологии**: PyTorch, Transformers, vidore/colpali
- **Функции**:
  - Обработка изображений в PDF документах
  - Визуальное понимание таблиц, графиков, диаграмм
  - Векторизация изображений для поиска
  - Автоматическое масштабирование (idle → off)

## ⚙️ Конфигурация

### Основные файлы конфигурации

#### 1. `docker-compose.local.yml`
Основной файл для запуска API и Worker с подключением к удаленным сервисам.

```yaml
services:
  morphik:
    build: .
    ports:
      - "8000:8000"
    entrypoint: ["/bin/sh", "-c", "exec uv run uvicorn core.api:app --host 0.0.0.0 --port 8000 --reload"]
    environment:
      - POSTGRES_URI=postgresql+asyncpg://morphik:morphik@135.181.106.12:5432/morphik
      - REDIS_HOST=135.181.106.12
      - OLLAMA_BASE_URL=http://135.181.106.12:11434
```

#### 2. `morphik.toml`
Конфигурация моделей и сервисов:

```toml
[registered_models]
ollama_llama = { model_name = "ollama/llama3.2:3b", api_base = "http://135.181.106.12:11434" }
ollama_embedding = { model_name = "ollama/nomic-embed-text", api_base = "http://135.181.106.12:11434" }

[completion]
model = "ollama_llama"

[embedding]
model = "ollama_embedding"
```

#### 3. `.env.local` (для UI)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚀 Запуск системы

### Предварительные требования
- Docker Desktop
- Node.js 18+
- Git

### Пошаговая инструкция

#### 1. Клонирование и переход в директорию
```bash
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_local/Test/Morphik_local
```

#### 2. Запуск API и Worker в Docker
```bash
# Остановить все существующие контейнеры
docker-compose down

# Запустить через правильный конфигурационный файл
docker-compose -f docker-compose.local.yml up -d

# Проверить статус
docker ps
```

#### 3. Запуск UI для разработки
```bash
cd ee/ui-component

# Установить зависимости (первый раз)
npm install

# Настроить переменные окружения
echo 'NEXT_PUBLIC_API_URL=http://localhost:8000' > .env.local

# Запустить UI
npm run dev
```

#### 4. Проверка работоспособности
- UI: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Проверка здоровья: `curl http://localhost:8000/health`

### Остановка системы
```bash
# Остановить UI
# Нажать Ctrl+C в терминале с UI

# Остановить Docker контейнеры
docker-compose -f docker-compose.local.yml down
```

## 🐳 Docker образы

### Текущие образы (необходимые)
| Образ | Размер | Описание |
|-------|--------|----------|
| morphik_local-morphik | 3GB | API сервер |
| morphik_local-worker | 3GB | Фоновые задачи |
| morphik_local-ui | 201MB | Production UI (опционально) |
| alpine | 8.5MB | Служебный образ для проверок |

### Удаленные образы (не нужны локально)
- postgres:* - используется удаленный
- redis:* - используется удаленный
- ollama/ollama - используется удаленный
- morphik_experimental-* - старые версии

### Очистка Docker
```bash
# Удалить неиспользуемые образы
docker image prune -a

# Полная очистка (осторожно!)
docker system prune -a --volumes
```

## 🤖 Управление моделями

### Принцип работы фильтрации
1. **Ollama модели** - всегда доступны (локальные на сервере 135.181.106.12)
2. **Внешние модели** - доступны только при наличии API ключей в базе данных
3. **Фильтрация** - происходит на backend в endpoint `/models`

### Добавление новых моделей
1. Откройте Settings в UI
2. Добавьте API ключ для провайдера (OpenAI, Anthropic, Google и т.д.)
3. Модели автоматически появятся в списке выбора

### Конфигурация моделей (morphik.toml)
```toml
[registered_models]
# Ollama модели (всегда доступны)
ollama_llama = { model_name = "ollama/llama3.2:3b", api_base = "http://135.181.106.12:11434" }
ollama_embedding = { model_name = "ollama/nomic-embed-text", api_base = "http://135.181.106.12:11434" }

# Внешние модели (требуют API ключи)
claude_opus = { model_name = "anthropic/claude-3-opus-20240229" }
claude_sonnet = { model_name = "anthropic/claude-3-5-sonnet-latest" }
# Раскомментируйте после добавления ключей:
# openai_gpt4 = { model_name = "gpt-4" }
# gemini_flash = { model_name = "gemini/gemini-2.5-flash" }
```

## 🔍 Решение проблем

### Проблема: CORS ошибки в браузере
**Решение**: Убедитесь, что API запущен и morphik.toml содержит правильные адреса:
```toml
ollama_llama = { model_name = "ollama/llama3.2:3b", api_base = "http://135.181.106.12:11434" }
```

### Проблема: API не может подключиться к БД
**Решение**: Проверьте доступность удаленного сервера:
```bash
nc -zv 135.181.106.12 5432  # PostgreSQL
nc -zv 135.181.106.12 6379  # Redis
nc -zv 135.181.106.12 11434 # Ollama
```

### Проблема: Docker контейнеры не запускаются
**Решение**: 
1. Проверьте логи: `docker-compose -f docker-compose.local.yml logs`
2. Пересоберите образы: `docker-compose -f docker-compose.local.yml build --no-cache`

### Проблема: UI не подключается к API
**Решение**: Проверьте .env.local в ee/ui-component:
```bash
cat ee/ui-component/.env.local
# Должно быть: NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 Мониторинг

### Просмотр логов
```bash
# API логи
docker logs -f morphik_local-morphik-1

# Worker логи  
docker logs -f morphik_local-worker-1

# UI логи (если запущен через npm)
# Смотрите в терминале где запущен npm run dev
```

### Проверка использования ресурсов
```bash
# CPU и память контейнеров
docker stats

# Размер образов
docker images | grep morphik
```

## 🔐 Безопасность

### Текущие настройки
- **Dev mode**: Включен для локальной разработки
- **JWT**: Используется для аутентификации
- **CORS**: Разрешены все origins (только для разработки!)

### Для production
1. Отключить dev_mode в morphik.toml
2. Настроить правильные CORS origins
3. Использовать секретные ключи из переменных окружения
4. Включить HTTPS

## 📝 Дополнительная информация

### Переменные окружения API
| Переменная | Значение | Описание |
|------------|----------|----------|
| POSTGRES_URI | postgresql+asyncpg://morphik:morphik@135.181.106.12:5432/morphik | Строка подключения к БД |
| REDIS_HOST | 135.181.106.12 | Адрес Redis сервера |
| REDIS_PORT | 6379 | Порт Redis |
| OLLAMA_BASE_URL | http://135.181.106.12:11434 | URL Ollama API |
| JWT_SECRET_KEY | your-secret-key-here | Ключ для JWT токенов |

### Полезные команды
```bash
# Перезапуск только API
docker-compose -f docker-compose.local.yml restart morphik

# Просмотр конфигурации контейнера
docker inspect morphik_local-morphik-1

# Выполнение команды внутри контейнера
docker exec -it morphik_local-morphik-1 bash

# Проверка сетевого взаимодействия
docker network ls
docker network inspect morphik_local_morphik-network
```

## 🔄 Обновление системы

### Обновление кода
```bash
git pull origin main
docker-compose -f docker-compose.local.yml build
docker-compose -f docker-compose.local.yml up -d
```

### Обновление зависимостей UI
```bash
cd ee/ui-component
npm update
npm audit fix
```

## 📚 Связанная документация
- [MORPHIK_ARCHITECTURE.md](./MORPHIK_ARCHITECTURE.md) - Общая архитектура проекта
- [DEVELOPMENT_ARCHITECTURE.md](./DEVELOPMENT_ARCHITECTURE.md) - Архитектура для разработки
- [docker-compose.local.yml](./docker-compose.local.yml) - Docker конфигурация
- [morphik.toml](./morphik.toml) - Конфигурация приложения

---

*Последнее обновление: 08.08.2025*
*Версия: 1.0.0*