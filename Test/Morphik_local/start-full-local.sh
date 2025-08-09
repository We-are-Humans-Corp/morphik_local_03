#!/bin/bash

echo "🚀 MORPHIK LOCAL DEVELOPMENT LAUNCHER"
echo "====================================="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Архитектура запуска:${NC}"
echo "┌─────────────────────────────────────────────────┐"
echo "│  Локально (Mac)           Удаленно (Сервер)     │"
echo "├─────────────────────────────────────────────────┤"
echo "│  UI (:3001) ─┐                                  │"
echo "│              ├→ API в Docker (:8001) ─┐         │"
echo "│                                        ├→ PostgreSQL"
echo "│                                        ├→ Redis    "
echo "│                                        └→ Ollama   "
echo "└─────────────────────────────────────────────────┘"
echo ""

# Шаг 1: Запуск API в Docker
echo -e "${YELLOW}[1/3] Запускаем API в Docker...${NC}"
./start-docker-api.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Ошибка при запуске API${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ API успешно запущен в Docker${NC}"
echo ""

# Шаг 2: Настройка UI
echo -e "${YELLOW}[2/3] Настраиваем UI...${NC}"
cd ee/ui-component

# Копируем правильный env файл
cp .env.docker-api .env.local
echo -e "${GREEN}✅ Переменные окружения настроены${NC}"

# Устанавливаем зависимости если нужно
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Устанавливаем зависимости UI...${NC}"
    npm install
fi

# Шаг 3: Запуск UI
echo ""
echo -e "${YELLOW}[3/3] Запускаем UI...${NC}"
npm run dev &
UI_PID=$!

cd ../..

# Ждем запуска UI
sleep 7

# Финальная проверка
echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}✅ СИСТЕМА УСПЕШНО ЗАПУЩЕНА!${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""
echo "📍 Доступные сервисы:"
echo "   • UI: http://localhost:3001"
echo "   • API: http://localhost:8001"
echo "   • API Docs: http://localhost:8001/docs"
echo ""
echo "🔧 Полезные команды:"
echo "   • Логи API: docker-compose -f docker-compose.local-api.yml logs -f"
echo "   • Перезапуск API: docker-compose -f docker-compose.local-api.yml restart"
echo "   • Остановить все: ./stop-all-local.sh"
echo ""
echo "💡 Откройте браузер: http://localhost:3001"
echo ""
echo -e "${YELLOW}Нажмите Ctrl+C для остановки UI${NC}"

# Ждем завершения
wait $UI_PID