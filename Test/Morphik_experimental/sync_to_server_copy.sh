#!/bin/bash

# Скрипт для синхронизации локальной версии с промежуточной копией для сервера

SOURCE_DIR="/Users/fedor/PycharmProjects/PythonProject/Morphik_local/Morphik_local"
TARGET_DIR="/Users/fedor/PycharmProjects/PythonProject/Morphik_server_135.181.106.12"

echo "🔄 Синхронизация Morphik_local -> Morphik_server_135.181.106.12"
echo "Источник: $SOURCE_DIR"
echo "Назначение: $TARGET_DIR"
echo ""

# Создаем целевую директорию если не существует
mkdir -p "$TARGET_DIR"

# Синхронизация с исключениями
rsync -av --delete \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='.env' \
  --exclude='*.log' \
  --exclude='.pytest_cache' \
  --exclude='*.pyc' \
  --exclude='.DS_Store' \
  --exclude='docker-images/' \
  --exclude='dump.sql' \
  "$SOURCE_DIR/" \
  "$TARGET_DIR/"

echo ""
echo "✅ Синхронизация завершена!"
echo ""
echo "Следующие шаги:"
echo "1. cd $TARGET_DIR"
echo "2. git add ."
echo "3. git commit -m 'Ваше сообщение'"
echo "4. git push origin main"