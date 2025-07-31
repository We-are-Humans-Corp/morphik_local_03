# Git Deployment Setup для Morphik

## Текущая архитектура деплоя

### 1. Репозитории

**Основной репозиторий**: https://github.com/We-are-Humans-Corp/Morphik_01.git
**Репозиторий для деплоя на сервер**: https://github.com/We-are-Humans-Corp/Morphik_local.git

### 2. Схема деплоя

```
Локальная разработка (Morphik_01) 
    ↓ git push
GitHub (Morphik_local)
    ↓ git pull
Сервер (135.181.106.12)
```

### 3. SSH доступ к серверу

```bash
# Пользователь и IP
SERVER_USER="root"
SERVER_IP="135.181.106.12"

# SSH подключение
ssh root@135.181.106.12
```

### 4. Процесс деплоя

#### Автоматический деплой (рекомендуется)

Используйте готовые скрипты:

```bash
# Полный деплой с Docker образами
./deploy_all_to_server.sh

# Быстрый деплой только кода с проверкой статуса
./deploy_and_check.sh
```

#### Ручной деплой

1. **Локально - пуш в GitHub:**
```bash
cd morphik-core
git add .
git commit -m "Your commit message"
git push origin main
```

2. **На сервере - получение изменений:**
```bash
ssh root@135.181.106.12
cd /opt/morphik
git pull origin main
docker-compose -f docker-compose-official.yml down
docker-compose -f docker-compose-official.yml up -d
```

### 5. Скрипты для деплоя

#### deploy_and_check.sh
- Пушит код в GitHub
- Подключается по SSH к серверу
- Делает git pull
- Перезапускает Docker контейнеры
- Проверяет статус всех сервисов
- Показывает подробный отчет о состоянии сервера

#### deploy_all_to_server.sh
- Сохраняет Docker образы локально
- Пушит код в GitHub
- Копирует Docker образы на сервер через SCP
- Загружает образы на сервере
- Перезапускает все сервисы

### 6. Структура на сервере

```
/opt/morphik/
├── docker-compose-official.yml
├── morphik-core/
│   ├── core/
│   ├── migrations/
│   └── ...
├── .env
└── docker-images/ (временная папка для образов)
```

### 7. Настройка SSH ключей (если еще не настроено)

1. **Генерация SSH ключа локально:**
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

2. **Копирование ключа на сервер:**
```bash
ssh-copy-id root@135.181.106.12
```

3. **Проверка подключения:**
```bash
ssh root@135.181.106.12 "echo 'SSH работает!'"
```

### 8. GitHub настройки

Для работы с репозиторием нужен доступ к:
- https://github.com/We-are-Humans-Corp/Morphik_local

Убедитесь, что у вас есть права на push в этот репозиторий.

### 9. Переменные окружения на сервере

На сервере автоматически создается `.env` файл с:
- `DATABASE_URL`
- `ANTHROPIC_API_KEY`
- `JWT_SECRET_KEY` (генерируется автоматически)
- `SESSION_SECRET_KEY` (генерируется автоматически)
- `MODE=self_hosted`

### 10. Проверка деплоя

После деплоя проверьте:
- UI: http://135.181.106.12:3000
- API: http://135.181.106.12:8000
- API Docs: http://135.181.106.12:8000/docs

Тестовый пользователь:
- Username: testuser
- Password: testpass123

### Важные замечания

1. **Два репозитория**: Разработка ведется в `Morphik_01`, деплой идет через `Morphik_local`
2. **SSH доступ**: Используется root пользователь (в production рекомендуется создать отдельного пользователя)
3. **Автоматизация**: Скрипты деплоя автоматизируют весь процесс
4. **Docker**: Все сервисы запускаются в Docker контейнерах
5. **Миграции**: Автоматически выполняются при деплое