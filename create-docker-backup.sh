#!/bin/bash

# Создаем резервную копию текущих рабочих Docker образов

echo "📦 Создаем бэкап текущих Docker образов..."

BACKUP_DIR="docker-images-backup"
mkdir -p $BACKUP_DIR

# Сохраняем образы
echo "💾 Сохраняем morphik-ui..."
docker save morphik_experimental-ui:latest | gzip > $BACKUP_DIR/morphik-ui.tar.gz

echo "💾 Сохраняем morphik-api..."
docker save morphik_experimental-morphik:latest | gzip > $BACKUP_DIR/morphik-api.tar.gz

echo "💾 Сохраняем morphik-worker..."
docker save morphik_experimental-worker:latest | gzip > $BACKUP_DIR/morphik-worker.tar.gz

echo "💾 Сохраняем morphik-postgres..."
docker save morphik_experimental-postgres:latest | gzip > $BACKUP_DIR/morphik-postgres.tar.gz

# Показываем размеры
echo -e "\n📊 Размеры образов:"
du -h $BACKUP_DIR/*.tar.gz

# Создаем README для образов
cat > $BACKUP_DIR/README.md << EOF
# Docker Images Backup

Дата создания: $(date)

## Образы:
- morphik-ui.tar.gz - Frontend UI
- morphik-api.tar.gz - Backend API
- morphik-worker.tar.gz - Background worker
- morphik-postgres.tar.gz - Database with pgvector

## Восстановление:
\`\`\`bash
docker load < morphik-ui.tar.gz
docker load < morphik-api.tar.gz
docker load < morphik-worker.tar.gz
docker load < morphik-postgres.tar.gz
\`\`\`
EOF

echo -e "\n✅ Готово! Образы сохранены в $BACKUP_DIR/"
echo "⚠️  Эти файлы слишком большие для обычного Git"
echo "💡 Используйте Git LFS или создайте GitHub Release"