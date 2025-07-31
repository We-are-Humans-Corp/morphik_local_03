#!/bin/bash

# Скрипт для запуска ВСЕЙ системы Morphik одной командой
# Запускает: Docker контейнеры + локальный UI

set -e

echo "🚀 Запуск всей системы Morphik..."
echo ""

# 1. Запуск Docker контейнеров
echo "🐳 Запуск Docker контейнеров..."
docker compose down
docker compose --profile ollama up -d --no-build

# 2. Ожидание запуска контейнеров
echo ""
echo "⏳ Ожидание запуска сервисов..."
sleep 10

# 3. Проверка статуса
echo ""
echo "📊 Статус Docker контейнеров:"
docker compose ps

# 4. Запуск локального UI
echo ""
echo "🖥️  Запуск UI..."
cd ee/ui-component

# Убиваем старый процесс UI если есть
pkill -f "next-server" || true

# Запускаем UI в фоне
nohup npm run dev > /tmp/morphik-ui.log 2>&1 &
UI_PID=$!

echo "✅ UI запущен (PID: $UI_PID)"
echo "📝 Логи UI: /tmp/morphik-ui.log"

# 5. Финальная информация
echo ""
echo "✅ Вся система Morphik запущена!"
echo ""
echo "🌐 Доступ к сервисам:"
echo "   - UI: http://localhost:3000"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Команды:"
echo "   tail -f /tmp/morphik-ui.log   # Логи UI"
echo "   docker compose logs -f         # Логи Docker"
echo "   ./stop-all.sh                  # Остановить всё"
echo ""