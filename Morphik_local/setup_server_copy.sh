#!/bin/bash

# Скрипт для первоначальной настройки промежуточной копии

SERVER_COPY_DIR="/Users/fedor/PycharmProjects/PythonProject/Morphik_server_135.181.106.12"

echo "🔧 Настройка промежуточной копии для сервера"
echo ""

# Инициализация git если нужно
if [ ! -d "$SERVER_COPY_DIR/.git" ]; then
    echo "📁 Инициализация git репозитория..."
    cd "$SERVER_COPY_DIR"
    git init
    git remote add origin https://github.com/We-are-Humans-Corp/Morphik_local.git
    
    # Получаем актуальное состояние из GitHub
    echo "📥 Получение текущего состояния из GitHub..."
    git fetch origin main
    git reset --hard origin/main
    
    echo "✅ Git репозиторий настроен"
else
    echo "✅ Git репозиторий уже существует"
fi

# Создаем .env файл для сервера если его нет
if [ ! -f "$SERVER_COPY_DIR/.env" ]; then
    echo ""
    echo "📝 Создаем .env файл для сервера..."
    cat > "$SERVER_COPY_DIR/.env" << 'EOF'
JWT_SECRET_KEY=your-secret-key-8b3d4f2ea1e4c9a5b7d6f3e2c1a8b5d4f7e9c2b6a4d8f1e3c7b9a5d2f6e8c4
JWT_ALGORITHM=HS256
POSTGRES_USER=morphik
POSTGRES_PASSWORD=morphik123
POSTGRES_DB=morphik_db
POSTGRES_URI=postgresql+asyncpg://morphik:morphik123@postgres:5432/morphik_db
REDIS_HOST=redis
REDIS_PORT=6379
ANTHROPIC_API_KEY=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
EOF
    echo "✅ .env файл создан"
fi

echo ""
echo "🎉 Настройка завершена!"
echo ""
echo "Структура проектов:"
echo "├── Morphik_local/           # Для локальной разработки"
echo "└── Morphik_server_135.181.106.12/  # Для деплоя на сервер"
echo ""
echo "Используйте:"
echo "- ./sync_to_server_copy.sh   # Для синхронизации изменений"
echo "- ./deploy_to_production.sh  # Для полного деплоя"