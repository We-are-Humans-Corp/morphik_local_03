#!/bin/bash

echo "🚀 Starting UI with Docker API connection"
echo "=========================================="

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

cd ee/ui-component

# Копируем правильный env файл
echo -e "${YELLOW}📋 Настраиваем переменные окружения для Docker API...${NC}"
cp .env.docker-api .env.local

# Проверяем что API доступен
echo -e "${YELLOW}🔍 Проверяем доступность API на localhost:8001...${NC}"
if curl -s http://localhost:8001/docs > /dev/null; then
    echo -e "${GREEN}✅ API доступен!${NC}"
else
    echo -e "${RED}❌ API не доступен на localhost:8001${NC}"
    echo "Запустите сначала API командой:"
    echo "cd ../.. && ./start-docker-api.sh"
    exit 1
fi

# Устанавливаем зависимости если нужно
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Устанавливаем зависимости...${NC}"
    npm install
fi

# Запускаем UI
echo -e "${GREEN}✅ Запускаем UI...${NC}"
npm run dev &

# Ждем запуска
sleep 5

echo ""
echo -e "${GREEN}✅ Система запущена!${NC}"
echo ""
echo "📍 UI доступен по адресу: http://localhost:3001"
echo "📍 API доступен по адресу: http://localhost:8001"
echo "📚 API документация: http://localhost:8001/docs"
echo ""
echo "🔗 Архитектура:"
echo "   UI (localhost:3001) → API в Docker (localhost:8001) → Удаленные сервисы (135.181.106.12)"
echo ""
echo "💡 Совет: Откройте браузер и перейдите на http://localhost:3001"