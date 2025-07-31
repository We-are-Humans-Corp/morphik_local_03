# Morphik - Рабочая версия

## Быстрый запуск

```bash
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_local/Test/Morphik_local
docker compose --profile ollama up -d
```

## Остановка

```bash
docker compose down
```

## Доступ к системе

- **UI**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Учетные данные

- Username: `fedor`
- Password: `usertest1`

Или:
- Username: `testuser`
- Password: `testpassword123`

## Что исправлено в этой версии

- Заменены все URL с api.morphik.ai на localhost:8000
- Исправлена проблема с подключением UI к API
- Настроены правильные переменные окружения для Docker

## Важно

- При первом запуске в браузере очистите кеш (Cmd+Shift+R на Mac или Ctrl+Shift+R на Windows)
- Документы нужно загрузить заново через UI, так как файлы отсутствуют в storage/

## Структура

- `docker-compose.yml` - основной файл конфигурации
- `ee/ui-component/` - исходный код UI
- `core/` - исходный код API
- `storage/` - хранилище загруженных документов (пустое после пересборки)