# Deployment Chain: Local → GitHub → Server (135.181.106.12)

## 📋 Полная цепочка:

```
1. Локальная разработка (Docker) 
   ↓
2. Push в GitHub (./push_to_git.sh)
   ↓
3. Автоматический деплой на 135.181.106.12
```

## 🛠️ STEP 1: Настройка на сервере (ОДИН РАЗ)

SSH на ваш сервер:
```bash
ssh root@135.181.106.12
```

Выполните эти команды на сервере:
```bash
# 1. Перейти в нужную директорию
cd /opt

# 2. Клонировать репозиторий
git clone https://github.com/We-are-Humans-Corp/Morphik_local.git morphik
cd morphik

# 3. Создать production .env
cat > .env << EOF
DATABASE_URL=postgresql://morphik:morphik@postgres:5432/morphik
ANTHROPIC_API_KEY=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
JWT_SECRET_KEY=production-secret-key-change-this
SESSION_SECRET_KEY=production-session-key-change-this
MODE=self_hosted
EOF

# 4. Создать скрипт автодеплоя
cat > /opt/morphik/auto_deploy.sh << 'EOF'
#!/bin/bash
cd /opt/morphik
git pull origin main
docker-compose -f docker-compose-official.yml down
docker-compose -f docker-compose-official.yml up -d
sleep 30
docker exec morphik-morphik-1 python -m alembic upgrade head
docker exec morphik-morphik-1 psql -U morphik -d morphik -f /app/migrations/add_users_table.sql
echo "Deploy complete!"
EOF

chmod +x /opt/morphik/auto_deploy.sh

# 5. Запустить первый раз
./auto_deploy.sh
```

## 🚀 STEP 2: Ваш ежедневный workflow

### На локальной машине:

1. **Разработка локально:**
```bash
cd /Users/fedor/PycharmProjects/PythonProject/Sage_Claude/morphik-core
docker-compose -f docker-compose-official.yml up -d
# Тестируете на http://localhost:8000
```

2. **Когда готово - пуш в GitHub:**
```bash
./push_to_git.sh
```

3. **Деплой на сервер:**
```bash
# SSH на сервер
ssh root@135.181.106.12

# Запустить деплой
cd /opt/morphik
./auto_deploy.sh
```

## ✅ После деплоя доступно:

- **API**: http://135.181.106.12:8000
- **UI**: http://135.181.106.12:3000
- **Логин**: testuser / testpass123

## 🔄 Автоматизация (опционально)

Если хотите полную автоматизацию, добавьте в crontab на сервере:
```bash
# На сервере
crontab -e

# Добавить строку (проверка каждые 5 минут):
*/5 * * * * cd /opt/morphik && git pull origin main && docker-compose restart
```

Тогда сервер сам будет подтягивать изменения из GitHub!