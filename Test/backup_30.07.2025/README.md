# Morphik Final Version - 30.07.2025 (Обновлено)

## Быстрый запуск

```bash
./start-morphik.sh
```

Этот скрипт запустит ВСЮ систему Morphik без вопросов и сборок.

## Остановка

```bash
./stop-morphik.sh
```

## Что включено

- **API** (morphik_local-morphik) - порт 8000
- **UI** (morphik_local-ui) - порт 3000  
- **База данных** (morphik_local-postgres)
- **Redis** (redis:7-alpine)
- **Worker** (morphik_local-worker)
- **Ollama** (ollama/ollama) - порт 11434

## Доступ

- UI: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Логин

- Username: `fedor`
- Password: `usertest1`

Или:
- Username: `testuser`
- Password: `testpassword123`

## Что исправлено в этой версии (30.07.2025)

- Все URL изменены с api.morphik.ai на localhost:8000
- Исправлены проблемы подключения UI к API
- Добавлена поддержка INTERNAL_API_URL для серверных вызовов

## Образы Docker

Сохранены в этой папке:
- morphik-ui.tar.gz
- morphik-api.tar.gz
- morphik-worker.tar.gz
- morphik-postgres.tar.gz

## Восстановление образов

Если нужно загрузить образы заново:

```bash
docker load < morphik-ui.tar.gz
docker load < morphik-api.tar.gz
docker load < morphik-worker.tar.gz
docker load < morphik-postgres.tar.gz
```