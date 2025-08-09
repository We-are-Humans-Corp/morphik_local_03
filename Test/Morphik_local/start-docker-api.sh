#!/bin/bash

echo "🚀 Starting Morphik API in Docker (connecting to remote server 135.181.106.12)"
echo "================================================"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker не установлен${NC}"
    exit 1
fi

# Остановка существующего контейнера если есть
echo -e "${YELLOW}🔄 Останавливаем существующий контейнер если есть...${NC}"
docker-compose -f docker-compose.local-api.yml down 2>/dev/null

# Сборка образа
echo -e "${YELLOW}🔨 Собираем Docker образ...${NC}"
docker-compose -f docker-compose.local-api.yml build

# Запуск контейнера
echo -e "${GREEN}✅ Запускаем API контейнер...${NC}"
docker-compose -f docker-compose.local-api.yml up -d

# Ждем пока API запустится
echo -e "${YELLOW}⏳ Ждем запуска API...${NC}"
sleep 5

# Проверяем статус
if curl -s http://localhost:8001/docs > /dev/null; then
    echo -e "${GREEN}✅ API успешно запущен!${NC}"
    echo ""
    echo "📍 API доступен по адресу: http://localhost:8001"
    echo "📚 Документация: http://localhost:8001/docs"
    echo "🔗 UI должен подключаться к: http://localhost:8001"
    echo ""
    echo "🌐 Подключение к удаленным сервисам:"
    echo "   - PostgreSQL: 135.181.106.12:5432"
    echo "   - Redis: 135.181.106.12:6379"
    echo "   - Ollama: 135.181.106.12:11434"
    echo ""
    echo "📝 Логи: docker-compose -f docker-compose.local-api.yml logs -f"
    echo "🛑 Остановить: docker-compose -f docker-compose.local-api.yml down"
else
    echo -e "${RED}❌ API не отвечает. Проверьте логи:${NC}"
    echo "docker-compose -f docker-compose.local-api.yml logs"
    exit 1
fi