#!/bin/bash

# Простой запуск API без Docker
echo "🚀 Запуск Morphik API (простой режим)..."

# Переменные окружения для подключения к серверу
export DATABASE_URL="postgresql://morphik:morphik@135.181.106.12:5432/morphik"
export REDIS_URL="redis://135.181.106.12:6379"
export OLLAMA_BASE_URL="http://135.181.106.12:11434"
export PORT=8001

# Переход в директорию с кодом
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_local/Test/Morphik_local

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден!"
    exit 1
fi

echo "✅ Конфигурация:"
echo "   - API: http://localhost:8001"
echo "   - PostgreSQL: 135.181.106.12:5432"
echo "   - Redis: 135.181.106.12:6379"
echo "   - Ollama: 135.181.106.12:11434"

# Запуск API
python3 -m uvicorn core.api:app --host 0.0.0.0 --port 8001 --reload