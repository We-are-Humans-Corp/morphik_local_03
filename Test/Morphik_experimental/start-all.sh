#!/bin/bash

# Скрипт для запуска всего стека Morphik
# Включает: PostgreSQL, Redis, API, Worker, UI и опционально Ollama

set -e

echo "🚀 Запуск Morphik..."
echo ""

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    exit 1
fi

# Проверка Docker Compose
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose не установлен!"
    exit 1
fi

# Парсинг аргументов
WITH_OLLAMA=false
REBUILD=false
DETACHED=true

for arg in "$@"; do
    case $arg in
        --with-ollama)
            WITH_OLLAMA=true
            shift
            ;;
        --rebuild)
            REBUILD=true
            shift
            ;;
        --logs)
            DETACHED=false
            shift
            ;;
        --help)
            echo "Использование: ./start-all.sh [опции]"
            echo ""
            echo "Опции:"
            echo "  --with-ollama  Запустить с локальным Ollama"
            echo "  --rebuild      Пересобрать все образы"
            echo "  --logs         Показать логи (не в фоне)"
            echo "  --help         Показать эту справку"
            echo ""
            echo "Примеры:"
            echo "  ./start-all.sh                    # Запуск всех сервисов"
            echo "  ./start-all.sh --with-ollama      # Запуск с Ollama"
            echo "  ./start-all.sh --rebuild --logs   # Пересборка и логи"
            exit 0
            ;;
    esac
done

# Проверка .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден. Создаю из примера..."
    cp .env.example .env
    echo "📝 Пожалуйста, отредактируйте .env файл и запустите скрипт снова."
    exit 1
fi

# Остановка старых контейнеров
echo "🛑 Остановка существующих контейнеров..."
docker compose down

# Сборка образов если нужно
if [ "$REBUILD" = true ]; then
    echo "🔨 Пересборка образов..."
    BUILD_FLAG="--build"
else
    BUILD_FLAG=""
    echo "📦 Используем существующие образы..."
fi

# Запуск сервисов
if [ "$WITH_OLLAMA" = true ]; then
    echo "🚀 Запуск всех сервисов включая Ollama..."
    PROFILE="--profile ollama"
else
    echo "🚀 Запуск основных сервисов..."
    PROFILE=""
fi

if [ "$DETACHED" = true ]; then
    if [ "$REBUILD" = false ]; then
        docker compose $PROFILE up -d --no-build
    else
        docker compose $PROFILE up -d $BUILD_FLAG
    fi
    
    # Ожидание запуска
    echo ""
    echo "⏳ Ожидание запуска сервисов..."
    sleep 10
    
    # Проверка статуса
    echo ""
    echo "📊 Статус сервисов:"
    docker compose ps
    
    # Загрузка моделей Ollama если нужно
    if [ "$WITH_OLLAMA" = true ]; then
        echo ""
        echo "📦 Проверка моделей Ollama..."
        docker exec morphik_local-ollama-1 ollama list || echo "Модели еще загружаются..."
        
        # Загрузка базовых моделей
        echo "📥 Загрузка необходимых моделей..."
        docker exec morphik_local-ollama-1 ollama pull llama3.2:3b || true
        docker exec morphik_local-ollama-1 ollama pull nomic-embed-text || true
    fi
    
    echo ""
    echo "✅ Morphik запущен!"
    echo ""
    echo "🌐 Доступ к сервисам:"
    echo "   - UI: http://localhost:3000"
    echo "   - API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo ""
    echo "📋 Полезные команды:"
    echo "   docker compose logs -f        # Просмотр логов"
    echo "   docker compose ps             # Статус сервисов"
    echo "   docker compose down           # Остановка всех сервисов"
    echo ""
else
    # Запуск с выводом логов
    docker compose $PROFILE up $BUILD_FLAG
fi