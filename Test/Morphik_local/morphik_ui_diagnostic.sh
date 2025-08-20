#!/bin/bash

# Morphik UI Diagnostic Script
# Проверяет текущее состояние UI и выявляет проблемы

echo "🔍 Morphik UI Diagnostic Tool"
echo "=============================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Check Docker containers
echo "1️⃣ Проверка Docker контейнеров:"
echo "--------------------------------"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | grep -E "ui|morphik|worker" || echo "Контейнеры не найдены"
echo ""

# 2. Check UI version in package.json
echo "2️⃣ Версия UI в package.json:"
echo "-----------------------------"
if [ -f "ee/ui-component/package.json" ]; then
    version=$(grep '"version"' ee/ui-component/package.json | head -1 | cut -d'"' -f4)
    echo -e "${GREEN}Версия: $version${NC}"
    if [ "$version" = "0.4.7" ]; then
        echo -e "${GREEN}✅ Версия соответствует ожидаемой (0.4.7)${NC}"
    else
        echo -e "${YELLOW}⚠️ Версия отличается от ожидаемой (ожидается 0.4.7)${NC}"
    fi
else
    echo -e "${RED}❌ package.json не найден${NC}"
fi
echo ""

# 3. Check Next.js version
echo "3️⃣ Версия Next.js:"
echo "------------------"
if [ -f "ee/ui-component/package.json" ]; then
    nextjs=$(grep '"next"' ee/ui-component/package.json | head -1 | cut -d'"' -f4)
    echo -e "${GREEN}Next.js: $nextjs${NC}"
else
    echo -e "${RED}❌ Не удалось определить версию Next.js${NC}"
fi
echo ""

# 4. Check Docker image age
echo "4️⃣ Возраст Docker образов:"
echo "---------------------------"
docker images | grep -E "ui|morphik" | head -5
echo ""

# 5. Check if UI is accessible
echo "5️⃣ Доступность UI:"
echo "------------------"
for port in 3000 3001; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✅ UI доступен на порту $port${NC}"
    else
        echo -e "${YELLOW}⚠️ UI недоступен на порту $port${NC}"
    fi
done
echo ""

# 6. Check git status
echo "6️⃣ Git статус:"
echo "--------------"
git log --oneline -5
echo ""
current_branch=$(git branch --show-current)
echo "Текущая ветка: $current_branch"
echo ""

# 7. Check docker-compose file
echo "7️⃣ Используемый docker-compose:"
echo "--------------------------------"
if [ -f "docker-compose.local.yml" ]; then
    echo -e "${GREEN}✅ docker-compose.local.yml найден${NC}"
    grep -A 2 "ui:" docker-compose.local.yml | head -5
else
    echo -e "${RED}❌ docker-compose.local.yml не найден${NC}"
fi
echo ""

# 8. Check node_modules
echo "8️⃣ Состояние node_modules:"
echo "---------------------------"
if [ -d "ee/ui-component/node_modules" ]; then
    count=$(ls ee/ui-component/node_modules | wc -l)
    echo -e "${GREEN}✅ node_modules существует ($count пакетов)${NC}"
    # Check specific packages
    for pkg in "next" "react" "react-dom"; do
        if [ -d "ee/ui-component/node_modules/$pkg" ]; then
            echo "  ✅ $pkg установлен"
        else
            echo "  ❌ $pkg НЕ установлен"
        fi
    done
else
    echo -e "${RED}❌ node_modules не найден${NC}"
fi
echo ""

# Summary
echo "📊 ИТОГОВАЯ ДИАГНОСТИКА:"
echo "========================"

problems=0

# Check if UI container is running
if docker ps | grep -q "ui"; then
    echo -e "${GREEN}✅ UI контейнер запущен${NC}"
else
    echo -e "${RED}❌ UI контейнер НЕ запущен${NC}"
    problems=$((problems + 1))
fi

# Check if version is correct
if [ "$version" = "0.4.7" ]; then
    echo -e "${GREEN}✅ Версия UI актуальная${NC}"
else
    echo -e "${YELLOW}⚠️ Версия UI требует обновления${NC}"
    problems=$((problems + 1))
fi

# Check if UI is accessible
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✅ UI доступен через браузер${NC}"
else
    echo -e "${RED}❌ UI недоступен через браузер${NC}"
    problems=$((problems + 1))
fi

echo ""
if [ $problems -eq 0 ]; then
    echo -e "${GREEN}🎉 Все системы работают нормально!${NC}"
else
    echo -e "${YELLOW}⚠️ Обнаружено проблем: $problems${NC}"
    echo "Рекомендуется запустить: ./force_update_ui.sh"
fi