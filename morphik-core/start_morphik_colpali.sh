#!/bin/bash
set -e

echo "🚀 MORPHIK + COLPALI + MODAL STARTUP"
echo "===================================="

# 1. Применяем debug патчи
echo "1️⃣ Applying debug patches..."
python apply_debug_patches.py

# 2. Запускаем Docker контейнеры
echo "2️⃣ Starting Docker containers..."
docker-compose -f docker-compose.dev.yml up --build -d

# 3. Ждем готовности сервисов
echo "3️⃣ Waiting for services to be ready..."
sleep 30

# 4. Проверяем здоровье сервисов
echo "4️⃣ Checking service health..."
curl -f http://localhost:8000/health || echo "⚠️ Morphik API not ready yet"

echo ""
echo "✅ Startup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Deploy Modal API: modal deploy modal_colpali_api.py"
echo "2. Update MORPHIK_EMBEDDING_API_DOMAIN in .env with your Modal URL"
echo "3. Run tests: python test_colpali_integration.py"
echo ""
echo "📊 Monitor logs:"
echo "- Morphik: docker-compose -f docker-compose.dev.yml logs -f morphik"
echo "- Worker: docker-compose -f docker-compose.dev.yml logs -f worker"
echo ""
