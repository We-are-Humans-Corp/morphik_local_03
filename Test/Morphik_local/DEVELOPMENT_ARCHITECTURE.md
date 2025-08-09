# Morphik Development Architecture

## Текущая структура разработки

### 1. Общая архитектура
```
┌─────────────────────────────────────────────────────────────┐
│                     Production Environment                   │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ UI (Docker) │  │ API (Docker) │  │ Worker (Docker)  │  │
│  │ Port: 3000  │  │ Port: 8000   │  │                  │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
│         │                 │                    │             │
│         └─────────────────┴────────────────────┘            │
│                           │                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  PostgreSQL  │  │    Redis     │  │     Ollama       │  │
│  │  Port: 5432  │  │  Port: 6379  │  │  Port: 11434     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  Development Environment                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │         UI Development Server (Local)               │    │
│  │         Next.js Dev Mode                           │    │
│  │         Port: 3001                                 │    │
│  │         Hot Reload: ✓                              │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                  │
│                    Proxy (rewrites)                         │
│                           │                                  │
│                           ▼                                  │
│                   API (Port: 8000)                          │
└─────────────────────────────────────────────────────────────┘
```

### 2. Структура проекта
```
/Users/fedor/PycharmProjects/PythonProject/Morphik_local/
├── Test/
│   └── Morphik_local/                    # Рабочая директория
│       ├── docker-compose.yml            # Конфигурация всех сервисов
│       ├── ee/
│       │   └── ui-component/             # UI код (Next.js)
│       │       ├── app/                  # App Router
│       │       ├── components/           # React компоненты
│       │       ├── hooks/                # Custom hooks
│       │       ├── contexts/             # React contexts
│       │       ├── lib/                  # Утилиты
│       │       ├── public/               # Статические файлы
│       │       ├── next.config.mjs       # Конфигурация Next.js
│       │       ├── package.json          # Зависимости
│       │       └── .env.local            # Переменные окружения
│       ├── core/                         # Backend код
│       │   ├── api.py                    # FastAPI endpoints
│       │   ├── services/                 # Бизнес-логика
│       │   └── storage/                  # Работа с файлами
│       └── start-dev-ui.sh               # Скрипт запуска dev UI
```

### 3. Режимы работы

#### Production Mode (Docker)
- **URL**: http://localhost:3000
- **Все сервисы** запущены в Docker контейнерах
- **Стабильная версия** для тестирования
- Изменения требуют пересборки Docker образа

#### Development Mode (Hybrid)
- **URL**: http://localhost:3001
- **UI запущен локально** с hot reload
- **Backend сервисы** остаются в Docker
- Изменения в UI видны мгновенно
- API запросы проксируются через Next.js

### 4. Конфигурация проксирования (next.config.mjs)
```javascript
async rewrites() {
  return [
    { source: '/query', destination: 'http://localhost:8000/query' },
    { source: '/api/v1/:path*', destination: 'http://localhost:8000/api/v1/:path*' },
    { source: '/auth/:path*', destination: 'http://localhost:8000/auth/:path*' },
    { source: '/models', destination: 'http://localhost:8000/models' },
    // ... другие маршруты
  ]
}
```

### 5. Команды для разработки

#### Запуск production версии:
```bash
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_local/Test/Morphik_local
docker-compose up -d
```

#### Запуск development UI:
```bash
cd ee/ui-component
npm run dev
# или использовать скрипт:
./start-dev-ui.sh
```

#### Проверка статуса:
```bash
# Docker контейнеры
docker ps

# Dev UI процесс
lsof -i :3001
```

### 6. Git Workflow

#### Текущая ветка для экспериментов:
```bash
git checkout experiment-feature
```

#### Основная ветка:
```bash
git checkout main
```

### 7. Учетные данные для тестирования

**Тестовый пользователь:**
- Username: `ui_test_1754584705`
- Password: `password123`

### 8. Решенные проблемы

1. **CORS ошибки** - решено через proxy в next.config.mjs
2. **Symlink node_modules** - UI запускается из оригинальной директории
3. **Порт 11434 занят** - остановлены конфликтующие контейнеры
4. **500 ошибки при логине** - добавлено логирование для отладки

### 9. Важные замечания

- **НЕ изменяйте** docker-compose.yml без необходимости
- **НЕ останавливайте** backend контейнеры при разработке UI
- **Используйте** порт 3001 для разработки, не 3000
- **Коммитьте** только после проверки работоспособности
- **Создавайте** новые ветки для экспериментальных изменений

### 10. Переменные окружения

#### .env.local (для dev UI):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 11. Мониторинг и отладка

#### Логи Docker контейнеров:
```bash
docker logs morphik_local-morphik-1 -f    # API логи
docker logs morphik_local-ui-1 -f         # Production UI логи
```

#### Логи Dev UI:
- Отображаются в терминале где запущен `npm run dev`
- Или в файле `/tmp/ui-dev.log`

### 12. Полезные команды

```bash
# Перезапуск всех сервисов
docker-compose restart

# Пересборка конкретного сервиса
docker-compose up -d --build morphik

# Очистка Docker ресурсов
docker system prune -a

# Проверка API
curl http://localhost:8000/models

# Тест аутентификации
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "ui_test_1754584705", "password": "password123"}'
```

---

Эта архитектура позволяет быстро разрабатывать UI с мгновенным просмотром изменений, сохраняя при этом стабильную backend инфраструктуру.