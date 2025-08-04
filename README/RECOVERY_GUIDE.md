# Руководство по восстановлению проекта Morphik

## Быстрое восстановление с нуля

### 1. Клонирование репозитория
```bash
git clone https://github.com/We-are-Humans-Corp/Morphik_local_02.git
cd Morphik_local_02
```

### 2. Восстановление Docker образов

#### Вариант A: Загрузка образов из GitHub Release (рекомендуется)
```bash
# Скачайте образы из последнего релиза
# https://github.com/We-are-Humans-Corp/Morphik_local_02/releases

# Загрузите образы в Docker
docker load < morphik-ui.tar.gz
docker load < morphik-api.tar.gz
docker load < morphik-worker.tar.gz
docker load < morphik-postgres.tar.gz
```

#### Вариант B: Сборка образов с нуля
```bash
cd Morphik_local
docker-compose build
```

### 3. Настройка окружения
```bash
# Создайте .env файл с необходимыми переменными
cp morphik.docker.toml morphik.toml
# Отредактируйте morphik.toml под ваши нужды
```

### 4. Запуск проекта
```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

## Структура проекта

### Основные компоненты:
- **morphik-ui**: Frontend приложение (порт 3000)
- **morphik-api**: Backend API (порт 8080)
- **morphik-worker**: Background worker для обработки задач
- **morphik-postgres**: PostgreSQL с pgvector расширением

### Важные файлы:
- `docker-compose.yml` - основная конфигурация Docker
- `morphik.toml` - конфигурация приложения
- `dockerfile` - Dockerfile для API
- `postgres.dockerfile` - Dockerfile для БД с pgvector
- `ee/ui-component/Dockerfile` - Dockerfile для UI

## Проверка работоспособности

1. **UI доступен по адресу**: http://localhost:3000
2. **API доступен по адресу**: http://localhost:8080
3. **Проверка здоровья API**: http://localhost:8080/health

## Бэкап данных

### Создание бэкапа БД:
```bash
docker exec morphik-postgres pg_dump -U postgres morphik > backup.sql
```

### Восстановление БД:
```bash
docker exec -i morphik-postgres psql -U postgres morphik < backup.sql
```

### Создание бэкапа образов:
```bash
./create-docker-backup.sh
```

## Устранение проблем

### Если контейнеры не запускаются:
```bash
# Остановить все контейнеры
docker-compose down

# Удалить volumes (ВНИМАНИЕ: удалит данные!)
docker-compose down -v

# Перезапустить
docker-compose up -d
```

### Проверка логов:
```bash
docker-compose logs morphik-api
docker-compose logs morphik-ui
docker-compose logs morphik-worker
docker-compose logs morphik-postgres
```

## Контакты для поддержки

При возникновении проблем обращайтесь в Issues репозитория:
https://github.com/We-are-Humans-Corp/Morphik_local_02/issues