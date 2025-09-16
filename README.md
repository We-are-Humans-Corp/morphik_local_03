# AI-Powered Document Intelligence Platform

[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](https://github.com/We-are-Humans-Corp/Morphik_local)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![Modal](https://img.shields.io/badge/GPU-Modal.com-purple.svg)](https://modal.com)

AI-native platform for processing visually rich documents with multimodal understanding. 


## 🎯 Зачем нужна эта система

### Проблемы, которые решает 

1. **Визуальное понимание документов**
   - Традиционные RAG системы теряют 60% информации из PDF (графики, таблицы, диаграммы)
   - ColPali на GPU понимает визуальный контекст без OCR
   - Поиск по смыслу изображений, а не только тексту

2. **Экономия на инфраструктуре**
   - GPU A100 стоит $4/час постоянно vs $0.012/мин на Modal.com
   - Auto-scaling: платим только за реальное использование
   - Экономия до 90% на GPU ресурсах

3. **Enterprise-ready архитектура**
   - Multi-tenancy через app_id
   - JWT аутентификация с user scoping
   - Изоляция данных между приложениями
   - Готовность к масштабированию

4. **Гибридная обработка**
   - Локальные LLM через Ollama для конфиденциальности
   - Cloud модели (GPT-4, Claude) для сложных задач
   - ColPali на Modal.com для визуального анализа
   - Выбор модели под конкретную задачу

### Основные use cases

- **Анализ финансовых отчетов**: Извлечение данных из графиков и таблиц
- **Медицинские документы**: Понимание рентгеновских снимков и диаграмм
- **Техническая документация**: Поиск по схемам и чертежам
- **Научные статьи**: Анализ формул и визуализаций
- **Юридические документы**: Работа со сканами и подписями


## 🏗️ Архитектура

**Распределенная трехуровневая система с умной обработкой документов:**

```
┌─────────────────────────────────────────────────────────────┐
│                  ЛОКАЛЬНАЯ МАШИНА                            │
│   UI (React/Next.js) - Docker на порту 3000                 │
│   → Отправляет запросы с JWT токеном на сервер              │
└─────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│           HETZNER SERVER (135.181.106.12)                    │
│   • API (FastAPI) - порт 8000 с JWT аутентификацией         │
│   • Умная обработка: текст → Ollama, визуал → ColPali       │
│   • PostgreSQL, Redis, Ollama, MinIO, Worker                │
└─────────────────────────┬────────────────────────────────────┘
                         ↓ (только для PDF/изображений)
┌─────────────────────────────────────────────────────────────┐
│              MODAL.COM GPU CLOUD                             │
│   ColPali v1.2 на A100 для визуального понимания документов │
└─────────────────────────────────────────────────────────────┘
```

**Ключевые особенности:**
- ✅ JWT токены с реальным user_id из базы данных
- ✅ Умная логика выбора обработчика по типу документа
- ✅ Cross-domain CORS для безопасного соединения
- ✅ GPU используется только когда нужно (экономия 90%)

[Подробная архитектура →](./README/COMPLETE_DOCUMENTATION_v2.0.md#архитектура-v20)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 8GB RAM minimum
- Modal.com account (for GPU processing)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/We-are-Humans-Corp/Morphik_local.git
cd Morphik_local

# 2. Configure environment
cp hetzner-morphik/.env.example .env
# Edit .env with your API keys and server credentials

# 3. Start local UI
cd morphik-ui
docker-compose up -d

# 4. Connect to server (API already running)
# Server API: http://135.181.106.12:8000
# UI will connect automatically

# 5. Access UI
open http://localhost:3000
```

**Note:** API и все сервисы уже запущены на сервере Hetzner (135.181.106.12)

### Default Credentials
- **Username**: `demotest`
- **Password**: `demo123` 
- **API Docs**: http://135.181.106.12:8000/docs
- **Server**: 135.181.106.12 (Hetzner)

**Важно:** Система использует JWT токены с реальной аутентификацией

## 📊 Services & Ports

| Service | Port | Location | Description |
|---------|------|----------|-------------|
| **UI** | 3000 | Local Docker | Next.js 15 frontend с JWT auth |
| **API** | 8000 | Hetzner Server | FastAPI с умной обработкой документов |
| **Worker** | - | Hetzner Server | Arq background processing |
| **PostgreSQL** | 5432 | Hetzner Server | Database + pgvector + user auth |
| **Redis** | 6379 | Hetzner Server | Queue & cache |
| **Ollama** | 11434 | Hetzner Server | llama3.2 + nomic-embed для текста |
| **MinIO** | 32000 | Hetzner Server | S3-compatible storage |
| **ColPali** | HTTPS | Modal.com | GPU A100 для визуальных документов |

## 🔧 Конфигурация

### Структура проекта:
```
Morphik_local/
├── hetzner-morphik/     # Полная копия с сервера (backend)
├── morphik-ui/          # UI для локального запуска
├── README/              # Документация
└── .env                 # Главная конфигурация
```

### Основные файлы:
- `morphik.toml` - настройки моделей и сервисов
- `.env` - переменные окружения и API ключи
- `docker-compose.yml` - конфигурация Docker
- `core/routes/auth.py` - JWT аутентификация

[Подробная конфигурация →](./README/COMPLETE_DOCUMENTATION_v2.0.md#конфигурация)

## 📚 Documentation

- **[Complete Documentation v2.0](./README/COMPLETE_DOCUMENTATION_v2.0.md)** - Full system guide
- **[ColPali Setup](./README/COLPALI_COMPLETE_SETUP.md)** - GPU processing details
- **[Git Deployment](./README/GIT_DEPLOYMENT_SETUP.md)** - CI/CD workflow
- **[Changelog](./README/MORPHIK_CHANGELOG.md)** - Version history

## 🚢 Deployment

### Quick Deploy to Production

```bash
# Push to GitHub & deploy to server
git add . && \
git commit -m "feat: your changes" && \
git push origin main && \
ssh root@135.181.106.12 "cd /root/morphik-core && \
  git pull && \
  docker restart morphik-api"
```

### Deploy Modal Function

```bash
cd modal-morphik_test
modal deploy morphik_processor_fixed.py
```

**Note:** API автоматически перезапустится внутри Docker контейнера на сервере

## 🛠️ Troubleshooting

Частые проблемы и решения описаны в [документации](./README/COMPLETE_DOCUMENTATION_v2.0.md#troubleshooting).

Быстрая диагностика:
```bash
# Проверка локального UI
docker ps
curl http://localhost:3000

# Проверка API на сервере
curl http://135.181.106.12:8000/health
curl http://135.181.106.12:8000/auth/login  # JWT endpoint

# Логи API на сервере
ssh root@135.181.106.12 "docker logs morphik-api -f"

# Логи локального UI
docker logs morphik-ui -f
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request


## 🙏 Acknowledgments

- [ColPali](https://github.com/illuin-tech/colpali) - Visual document understanding
- [Modal.com](https://modal.com) - Serverless GPU infrastructure
- [FastAPI](https://fastapi.tiangolo.com) - Modern API framework
- [Next.js](https://nextjs.org) - React framework

