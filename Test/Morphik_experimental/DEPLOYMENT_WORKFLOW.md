# Workflow для деплоя Morphik

## Структура проектов

```
/Users/fedor/PycharmProjects/PythonProject/
├── Morphik_local/                    # Локальная разработка и тестирование
│   └── Morphik_local/
└── Morphik_server_135.181.106.12/    # Промежуточная копия для сервера
```

## Процесс работы

### 1. Локальная разработка
- Работаете в `Morphik_local/Morphik_local`
- Тестируете изменения локально с Docker
- Все изменения остаются в локальной версии

### 2. Перенос на промежуточную версию
```bash
# Синхронизация изменений
rsync -av --delete \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='.env' \
  /Users/fedor/PycharmProjects/PythonProject/Morphik_local/Morphik_local/ \
  /Users/fedor/PycharmProjects/PythonProject/Morphik_server_135.181.106.12/
```

### 3. Push в GitHub из промежуточной версии
```bash
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_server_135.181.106.12
git add .
git commit -m "Deploy: описание изменений"
git push origin main
```

### 4. Автоматический деплой на сервер
После push в GitHub, на сервере 135.181.106.12:
```bash
cd /opt/morphik
git pull origin main
docker compose down
docker compose --profile ollama up -d --build
```

## Скрипты автоматизации

### sync_to_server_copy.sh
```bash
#!/bin/bash
# Синхронизация локальной версии с промежуточной

rsync -av --delete \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='.env' \
  --exclude='*.log' \
  /Users/fedor/PycharmProjects/PythonProject/Morphik_local/Morphik_local/ \
  /Users/fedor/PycharmProjects/PythonProject/Morphik_server_135.181.106.12/

echo "✅ Синхронизация завершена"
```

### deploy_to_production.sh
```bash
#!/bin/bash
# Полный деплой на продакшн

# 1. Синхронизация с промежуточной версией
./sync_to_server_copy.sh

# 2. Коммит и push в GitHub
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_server_135.181.106.12
git add .
git commit -m "Deploy: $(date +%Y-%m-%d_%H:%M:%S)"
git push origin main

# 3. Деплой на сервер
ssh root@135.181.106.12 << 'EOF'
cd /opt/morphik
git pull origin main
docker compose down
docker compose --profile ollama up -d --build
docker compose ps
EOF

echo "🚀 Деплой завершен!"
```

## Преимущества такого подхода

1. **Изоляция**: Локальная версия полностью независима
2. **Безопасность**: Нет риска случайно запушить тестовые изменения
3. **Контроль**: Вы решаете, что и когда переносить на сервер
4. **История**: В промежуточной версии чистая git история для продакшна
5. **Откат**: Легко откатиться на предыдущую версию

## Важные замечания

- Держите `.env` файлы отдельно для каждой среды
- Не синхронизируйте логи и временные файлы
- Всегда проверяйте изменения перед деплоем
- Делайте бэкапы перед критическими изменениями