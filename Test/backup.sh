#!/bin/bash
# Скрипт для создания резервной копии перед изменениями

echo "🔒 Создание резервной копии Docker образов..."

# Создаём метку времени
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Архивируем предыдущий latest в archive
if [ -d "backups/latest" ] && [ "$(ls -A backups/latest)" ]; then
    echo "📦 Архивирование предыдущей версии..."
    mkdir -p "backups/archive/$TIMESTAMP"
    mv backups/latest/* "backups/archive/$TIMESTAMP/"
fi

# Сохраняем текущие образы
echo "💾 Сохранение текущих образов..."
docker save morphik_local-ui:latest > backups/latest/ui.tar
docker save morphik_local-morphik:latest > backups/latest/api.tar
docker save morphik_local-worker:latest > backups/latest/worker.tar
docker save morphik_local-postgres:latest > backups/latest/postgres.tar

# Сохраняем информацию о версии
echo "Backup created at: $TIMESTAMP" > backups/latest/version.txt
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" > backups/latest/containers_state.txt

echo "✅ Резервная копия создана в backups/latest/"
echo "📋 Предыдущие версии доступны в backups/archive/"