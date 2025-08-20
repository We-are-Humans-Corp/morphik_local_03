#!/bin/bash

# Force Update UI Script
# Принудительно обновляет UI до последней версии

echo "🚀 Morphik UI Force Update Tool"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Stop current containers
echo -e "${YELLOW}Шаг 1: Остановка текущих контейнеров...${NC}"
docker-compose -f docker-compose.local.yml down || docker-compose down
echo -e "${GREEN}✅ Контейнеры остановлены${NC}"
echo ""

# Step 2: Remove old UI images
echo -e "${YELLOW}Шаг 2: Удаление старых образов UI...${NC}"
docker images | grep ui | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
echo -e "${GREEN}✅ Старые образы удалены${NC}"
echo ""

# Step 3: Clean Docker cache
echo -e "${YELLOW}Шаг 3: Очистка Docker кэша...${NC}"
docker builder prune -f
echo -e "${GREEN}✅ Кэш очищен${NC}"
echo ""

# Step 4: Update dependencies
echo -e "${YELLOW}Шаг 4: Обновление зависимостей...${NC}"
cd ee/ui-component
rm -rf node_modules package-lock.json .next
npm cache clean --force
npm install
echo -e "${GREEN}✅ Зависимости обновлены${NC}"
cd ../..
echo ""

# Step 5: Build UI without cache
echo -e "${YELLOW}Шаг 5: Сборка UI без кэша...${NC}"
docker-compose -f docker-compose.local.yml build ui --no-cache
echo -e "${GREEN}✅ UI собран заново${NC}"
echo ""

# Step 6: Start containers
echo -e "${YELLOW}Шаг 6: Запуск контейнеров...${NC}"
docker-compose -f docker-compose.local.yml up -d
echo -e "${GREEN}✅ Контейнеры запущены${NC}"
echo ""

# Step 7: Wait for services to be ready
echo -e "${YELLOW}Шаг 7: Ожидание готовности сервисов...${NC}"
sleep 10

# Step 8: Verify services
echo -e "${YELLOW}Шаг 8: Проверка сервисов...${NC}"
echo ""

# Check containers
echo "Запущенные контейнеры:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep morphik
echo ""

# Check UI version
echo "Версия UI:"
grep '"version"' ee/ui-component/package.json | head -1
echo ""

# Check accessibility
echo "Проверка доступности:"
for port in 3000 8000; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✅ Сервис на порту $port доступен${NC}"
    else
        echo -e "${RED}❌ Сервис на порту $port недоступен${NC}"
    fi
done
echo ""

# Final message
echo "================================"
echo -e "${GREEN}🎉 Обновление завершено!${NC}"
echo ""
echo "Проверьте UI по адресу:"
echo "  http://localhost:3000"
echo ""
echo "API документация:"
echo "  http://localhost:8000/docs"
echo ""
echo "Логин для входа:"
echo "  Email: test@example.com"
echo "  Password: testpassword123"
echo ""
echo "Если UI все еще показывает старую версию:"
echo "1. Очистите кэш браузера (Ctrl+Shift+R)"
echo "2. Откройте в приватном/инкогнито режиме"
echo "3. Проверьте логи: docker-compose logs ui -f"