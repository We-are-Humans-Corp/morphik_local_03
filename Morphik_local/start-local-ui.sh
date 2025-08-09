#!/bin/bash
# Скрипт для запуска локальной версии UI на порту 3001

echo "🚀 Запуск локальной версии UI на порту 3001..."

cd /Users/fedor/PycharmProjects/PythonProject/Morphik_local/Morphik_local/ee/ui-component

# Устанавливаем переменные окружения для локальной разработки
export NODE_ENV=development
export PORT=3001
export NEXT_PUBLIC_API_URL=http://localhost:8000
export NEXT_PUBLIC_SOCKET_URL=ws://localhost:8000

# Проверяем наличие node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 Установка зависимостей..."
    npm install --legacy-peer-deps
fi

# Запускаем сервер разработки
echo "🔥 Запуск Next.js в режиме разработки..."
npm run dev -- -p 3001