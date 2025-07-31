# 🎯 ПРОСТАЯ СТРУКТУРА БЕЗ ПУТАНИЦЫ

## 📁 Новая структура:

```
Test/
├── infrastructure/           # 🔧 ОБЩИЕ СЕРВИСЫ (запускается ОДИН РАЗ)
│   ├── docker-compose.yml   # Ollama, Redis, PostgreSQL
│   └── README.md
│
├── Morphik_local/           # ✅ СТАБИЛЬНАЯ версия кода
├── Morphik_experimental/    # 🧪 ТЕСТОВАЯ версия кода
│
├── morphik_stable_clean.yml    # Запуск stable версии
└── morphik_experimental_clean.yml # Запуск experimental версии
```

## 🚀 Как использовать:

### 1️⃣ ОДИН РАЗ запустить инфраструктуру:
```bash
cd infrastructure
docker compose up -d

# Загрузить модели (если еще не загружены)
docker exec morphik_ollama_shared ollama pull llama3.2:3b
docker exec morphik_ollama_shared ollama pull nomic-embed-text
```

### 2️⃣ Запускать нужную версию:

**Для STABLE версии:**
```bash
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_local/Test
docker compose -f morphik_stable_clean.yml up -d
```
- UI: http://localhost:3000
- API: http://localhost:8000

**Для EXPERIMENTAL версии:**
```bash
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_local/Test
docker compose -f morphik_experimental_clean.yml up -d
```
- UI: http://localhost:3001
- API: http://localhost:8001

## ✅ Преимущества:

1. **Модели загружаются ОДИН РАЗ** и используются всеми версиями
2. **Нет путаницы** - инфраструктура отдельно, код отдельно
3. **Можно запускать обе версии одновременно** (разные порты)
4. **Экономия места** - одни модели для всех
5. **Простое переключение** между версиями

## 🛑 Остановка:

```bash
# Остановить версию
docker compose -f morphik_stable_clean.yml down
# или
docker compose -f morphik_experimental_clean.yml down

# Остановить инфраструктуру (только если больше не нужна)
cd infrastructure && docker compose down
```

## 💡 Итог:

- **infrastructure/** - запускается один раз, содержит ВСЕ модели и БД
- **Morphik_local/** - только код stable версии  
- **Morphik_experimental/** - только код experimental версии
- Версии используют ОБЩИЕ модели и сервисы, но РАЗНЫЕ базы данных