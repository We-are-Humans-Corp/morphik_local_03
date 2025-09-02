# 🧹 Morphik Project Cleanup Priority List

## 📊 Анализ текущего состояния
- **Общий размер проекта**: ~1.2GB
- **Основные потребители места**:
  - `ee/ui-component/node_modules`: ~890MB
  - `logs/`: 116MB (особенно telemetry)
  - `venv/`: 88MB
  - Большие файлы (GIF, логи): ~140MB

## 🔴 ВЫСОКИЙ ПРИОРИТЕТ (удалить немедленно)

### 1. Python Cache файлы (~5-10MB)
```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -o -name "*.pyo" -o -name "*.pyd" -delete
```

### 2. Большие логи (116MB)
```bash
# Очистить большие логи telemetry
echo "" > ./logs/telemetry/metrics.log  # 90MB
echo "" > ./logs/telemetry/traces.log   # 13MB
rm -f ./logs/*.log
rm -f ./docker-start.log
```

### 3. UI Backup (2.9MB) - устаревший бэкап
```bash
rm -rf ee/ui-component-backup-20250822
```

### 4. Временные и системные файлы
```bash
find . -name ".DS_Store" -delete
find . -name "*.tmp" -o -name "*.bak" -o -name "*.backup" -o -name "*.old" -delete
```

## 🟡 СРЕДНИЙ ПРИОРИТЕТ (можно удалить)

### 5. Дублирующие Docker конфигурации
Оставить только `docker-compose.local.yml`, удалить:
```bash
rm -f docker-compose.dev.yml        # старая dev версия
rm -f docker-compose.local-api.yml  # частичная конфигурация
rm -f docker-compose.run.yml        # старая run версия
```

### 6. Неиспользуемые скрипты запуска
```bash
# Удалить старые скрипты запуска (используем Docker)
rm -f start-api-python.sh
rm -f start-api-simple.sh
rm -f start-dev-ui.sh
rm -f start-docker-api.sh
rm -f setup-ssh-tunnels.sh
rm -f force_update_ui.sh           # UI теперь в Docker
rm -f morphik_ui_diagnostic.sh     # диагностика не нужна
```

### 7. Большой GIF файл (25MB)
```bash
rm -f db_atf_demo_hq.gif  # демо GIF не нужен в проде
```

### 8. Пустая директория official-morphik-ui (8.3MB)
```bash
rm -rf official-morphik-ui  # пустая/неиспользуемая
```

### 9. Виртуальное окружение Python (88MB)
```bash
rm -rf venv/  # если используете Docker, venv не нужен
```

## 🟢 НИЗКИЙ ПРИОРИТЕТ (обсудить перед удалением)

### 10. Старые документы в storage
```bash
# Проверить и удалить старые загрузки
ls -la storage/ingest_uploads/
# Удалить старые директории если не нужны
```

### 11. Дублирующая документация
- `README_GIT.md` - можно объединить с README.md
- `README_WORKING.md` - старые заметки
- `deploy_chain.md` - устаревшая инструкция
- `DOCKER.md` - можно интегрировать в README.md

### 12. Тестовые файлы
```bash
rm -f add_api_keys.js      # тестовый скрипт
rm -f check_auth.html       # тестовая страница
rm -f create_user.py        # можно делать через API
rm -f quick_setup.py        # старый setup
```

## ⚠️ НЕ УДАЛЯТЬ

### Критически важные файлы:
- ✅ `docker-compose.local.yml` - основная конфигурация
- ✅ `docker-compose.yml` - резервная конфигурация
- ✅ `morphik.toml` - конфигурация приложения
- ✅ `.env` - переменные окружения
- ✅ `Dockerfile` - образ Docker
- ✅ `pyproject.toml` - зависимости Python
- ✅ Все файлы в `core/` - основная логика
- ✅ `ee/ui-component/` - UI приложение
- ✅ `auth-service/` - сервис аутентификации

## 📝 Команда для безопасной очистки

```bash
#!/bin/bash
# Безопасная очистка Morphik проекта

echo "🧹 Начинаем очистку проекта Morphik..."

# 1. Python cache (безопасно)
echo "Удаляем Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -o -name "*.pyo" -delete

# 2. Системные файлы (безопасно)
echo "Удаляем системные файлы..."
find . -name ".DS_Store" -delete

# 3. Очистка логов (безопасно)
echo "Очищаем большие логи..."
echo "" > ./logs/telemetry/metrics.log
echo "" > ./logs/telemetry/traces.log

# 4. Удаление бэкапов (безопасно)
echo "Удаляем старые бэкапы..."
rm -rf ee/ui-component-backup-20250822

echo "✅ Безопасная очистка завершена!"
echo ""
echo "⚠️  Для дополнительной очистки выполните вручную:"
echo "  - Удаление дублирующих docker-compose файлов"
echo "  - Удаление venv/ если используете Docker"
echo "  - Удаление db_atf_demo_hq.gif (25MB)"
```

## 💡 Рекомендации

1. **Сначала выполните безопасную очистку** - это освободит ~120MB
2. **Проверьте docker-compose файлы** - оставьте только нужные
3. **Настройте ротацию логов** в Docker для предотвращения роста
4. **Добавьте .gitignore** для предотвращения коммита мусорных файлов:
```gitignore
__pycache__/
*.pyc
*.pyo
*.pyd
.DS_Store
*.log
*.tmp
*.bak
*.backup
*.old
venv/
.env
```

## 📊 Ожидаемый результат очистки

- **Высокий приоритет**: ~120MB
- **Средний приоритет**: ~125MB  
- **Низкий приоритет**: ~10MB
- **ИТОГО**: ~255MB (21% от текущего размера)

После очистки размер проекта уменьшится с 1.2GB до ~950MB.