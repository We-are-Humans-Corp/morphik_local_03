#!/bin/bash

echo "🚀 Запуск локального API..."

# Активация виртуального окружения
source venv/bin/activate

# Экспорт переменных окружения
export DATABASE_URL="postgresql://morphik:morphik@135.181.106.12:5432/morphik"
export REDIS_URL="redis://135.181.106.12:6379"
export OLLAMA_BASE_URL="http://135.181.106.12:11434"
export JWT_SECRET_KEY="your-secret-key"
export HOST="0.0.0.0"
export PORT="8001"

echo "✅ Конфигурация:"
echo "   - API: http://localhost:8001"
echo "   - DB: 135.181.106.12:5432"
echo "   - Redis: 135.181.106.12:6379"
echo "   - Ollama: 135.181.106.12:11434"
echo ""
echo "🔄 Hot reload активен"

# Запуск API
uvicorn core.api:app --host 0.0.0.0 --port 8001 --reload