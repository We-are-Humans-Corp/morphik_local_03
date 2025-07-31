#!/bin/bash

# Morphik Final Version - 19.07.2024
# Простой запуск всей системы без вопросов и сборок

echo "🚀 Запуск Morphik (версия 19.07.2024)..."

# Переход в основную директорию
cd "$(dirname "$0")/.."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    exit 1
fi

# Остановка существующих контейнеров
echo "🛑 Остановка старых контейнеров..."
docker compose down 2>/dev/null || true

# Запуск всех сервисов БЕЗ сборки
echo "🐳 Запуск контейнеров..."
docker compose --profile ollama up -d --no-build

# Ожидание
sleep 5

# Проверка статуса
echo ""
echo "📊 Статус сервисов:"
docker compose ps

echo ""
echo "✅ Morphik запущен!"
echo ""
echo "🌐 Доступ:"
echo "   UI: http://localhost:3000"
echo "   API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🔑 Логин: testuser / testpassword123"