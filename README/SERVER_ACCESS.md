# Доступы к серверу Morphik

## Архитектура системы

### Локальная разработка
- **Frontend UI**: http://localhost:3000 (Next.js Development Server)
- **API**: http://localhost:8000 (Docker Container)

### Hetzner сервер (135.181.106.12)
- **PostgreSQL**: порт 5432 (внутренний доступ)
- **Redis**: порт 6379 (внутренний доступ)
- **Ollama**: порт 11434 (внутренний доступ)
- **MinIO**: порт 9000 (внутренний доступ)

### RunPod GPU (Serverless)
- **ColPali Service**: https://api.runpod.ai/v2/fl73vpjsrfqhmn/runsync
- **GPU**: 24GB VRAM (автоматическое масштабирование)
- **Функция**: Обработка изображений в PDF документах

### API Endpoints

#### Локальная разработка (localhost:8000)
- `POST http://localhost:8000/auth/register` - Регистрация нового пользователя
- `POST http://localhost:8000/auth/login` - Вход в систему  
- `GET http://localhost:8000/auth/me` - Получить информацию о текущем пользователе
- `GET http://localhost:8000/v1/models` - Список доступных моделей
- `POST http://localhost:8000/v1/chat/completions` - Чат с AI
- `POST http://localhost:8000/v1/ingest/files` - Загрузка документов
- `GET http://localhost:8000/v1/documents` - Список документов
- `POST http://localhost:8000/v1/retrieve` - Поиск по документам

#### ColPali (визуальная обработка PDF)
- `POST https://api.runpod.ai/v2/fl73vpjsrfqhmn/runsync` - Обработка изображений в PDF
- Автоматически вызывается при загрузке документов с изображениями
- Требует RUNPOD_API_KEY в переменных окружения

### Примеры использования

#### Проверка доступности локального API
```bash
curl http://localhost:8000/health
```

#### Вход в систему (локальная разработка)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demotest",
    "password": "demo"
  }'
```

#### Получение списка моделей
```bash
curl http://localhost:8000/v1/models
```

#### Тест ColPali обработки (пример)
```bash
curl -X POST https://api.runpod.ai/v2/fl73vpjsrfqhmn/runsync \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "image": "base64_encoded_image_data"
    }
  }'
```

### Веб-интерфейс

Основной веб-интерфейс доступен по адресу: **http://localhost:3000** (для разработки)

Через веб-интерфейс доступны:
- Вход в систему (demotest/demo)
- Чат с различными AI моделями (Ollama, Claude при наличии API ключей)
- Загрузка и управление документами с ColPali обработкой
- Поиск по загруженным документам (включая визуальное содержимое)
- Настройки API ключей

### Учетные данные для входа

- **Username**: `demotest`
- **Password**: `demo`
- **User ID**: `8`

### Компоненты архитектуры

#### Локальные сервисы
- **UI (Development)**: http://localhost:3000
- **API**: http://localhost:8000  
- **Worker**: Фоновые задачи (Docker)

#### Удаленные сервисы (Hetzner 135.181.106.12)
- **PostgreSQL**: База данных с pgvector
- **Redis**: Кеш и очереди задач
- **Ollama**: LLM модели (llama3.2:3b, nomic-embed-text)
- **MinIO**: Объектное хранилище

#### GPU сервисы (RunPod)
- **ColPali**: Обработка изображений в PDF
- **Endpoint**: fl73vpjsrfqhmn
- **Масштабирование**: Автоматическое (idle → off)

### Примечания

- Система работает в режиме локальной разработки
- ColPali автоматически масштабируется при необходимости
- API ключи сохраняются в базе данных и привязаны к пользователю
- Все чаты и документы сохраняются в PostgreSQL