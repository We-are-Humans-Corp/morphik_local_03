# 🚀 Morphik v2.0 - AI-Powered Document Intelligence Platform

[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](https://github.com/We-are-Humans-Corp/Morphik_local)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![Modal](https://img.shields.io/badge/GPU-Modal.com-purple.svg)](https://modal.com)

AI-native platform for processing visually rich documents with multimodal understanding. Powered by ColPali on Modal.com GPU infrastructure.


## 🎯 Зачем нужна эта система

### Проблемы, которые решает Morphik v2.0

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

**Трехуровневая система:**
- 🖥️ **Локально**: UI (React), API (FastAPI), Worker - порты 3000, 8000
- ☁️ **Modal.com**: ColPali GPU обработка на A100
- 🗄️ **Hetzner**: PostgreSQL, Redis, Ollama - сервер 135.181.106.12

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
cd Morphik_local/modal-morphik_test

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start services
docker-compose up -d

# 4. Deploy Modal GPU function
modal deploy morphik_processor_fixed.py

# 5. Access UI
open http://localhost:3000
```

### Default Credentials
- **Username**: `demotest`
- **Password**: `demo`
- **API Docs**: http://localhost:8000/docs

## 📊 Services & Ports

| Service | Port | Location | Description |
|---------|------|----------|-------------|
| **UI** | 3000 | Local Docker | Next.js 15 frontend |
| **API** | 8000 | Local Docker | FastAPI backend |
| **PostgreSQL** | 5432 | Hetzner | Database + pgvector |
| **Redis** | 6379 | Hetzner | Queue & cache |
| **Ollama** | 11434 | Hetzner | Local LLM models |
| **MinIO** | 32000 | Hetzner | S3-compatible storage |
| **ColPali** | HTTPS | Modal.com | GPU processing |

## 🔧 Конфигурация

Основные файлы:
- `morphik.toml` - настройки моделей и сервисов
- `.env` - переменные окружения и API ключи
- `docker-compose.yml` - конфигурация Docker

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
cd /Users/fedor/PycharmProjects/PythonProject/Morphik_local && \
git add . && \
git commit -m "feat: your changes" && \
git push origin main && \
ssh root@135.181.106.12 "cd /opt/morphik && git pull && docker-compose restart"
```

### Deploy Modal Function

```bash
modal deploy morphik_processor_fixed.py
```

## 🛠️ Troubleshooting

Частые проблемы и решения описаны в [документации](./README/COMPLETE_DOCUMENTATION_v2.0.md#troubleshooting).

Быстрая диагностика:
```bash
# Проверка сервисов
docker ps
curl http://localhost:8000/health

# Логи
docker logs morphik-colpali-configured -f
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

