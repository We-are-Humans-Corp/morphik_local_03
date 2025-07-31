#!/bin/bash

# Скрипт для обновления Morphik на облачном сервере
# Использование: ./update_server.sh <server_ip> <ssh_user>

SERVER_IP=${1:-135.181.106.12}
SSH_USER=${2:-root}
PROJECT_DIR="/opt/morphik"

echo "🚀 Начинаем обновление Morphik на сервере $SERVER_IP"

# Команды для выполнения на сервере
ssh $SSH_USER@$SERVER_IP << 'ENDSSH'
set -e

echo "📍 Переходим в директорию проекта..."
cd $PROJECT_DIR || { echo "Ошибка: директория $PROJECT_DIR не найдена"; exit 1; }

echo "🛑 Останавливаем все сервисы..."
docker compose down

echo "🧹 Очищаем Docker кеш и старые образы..."
docker system prune -af --volumes
docker rmi $(docker images -q) 2>/dev/null || true

echo "📥 Получаем последние изменения из GitHub..."
git fetch origin
git reset --hard origin/main
git pull origin main

echo "🔧 Обновляем конфигурацию..."
# Если нужно сохранить локальный .env файл
if [ -f .env.backup ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

echo "🏗️ Пересобираем все образы..."
docker compose build --no-cache

echo "🚀 Запускаем обновленные сервисы..."
docker compose --profile ollama up -d

echo "⏳ Ждем запуска сервисов..."
sleep 30

echo "📦 Загружаем модели Ollama..."
docker exec -it ollama ollama pull llama3.2:3b || true
docker exec -it ollama ollama pull nomic-embed-text || true

echo "✅ Проверяем статус сервисов..."
docker compose ps

echo "🎉 Обновление завершено!"
ENDSSH

echo "✨ Скрипт выполнен. Проверьте сервер: http://$SERVER_IP:3000"