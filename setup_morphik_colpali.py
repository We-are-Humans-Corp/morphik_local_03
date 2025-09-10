#!/usr/bin/env python3
"""
Claude Code: Автоматическая настройка Morphik + ColPali + Modal
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def run_command(cmd, check=True, cwd=None):
    """Выполняет команду и возвращает результат"""
    print(f"🔧 Executing: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"❌ Error: {result.stderr}")
        sys.exit(1)
    return result

def create_file(path, content):
    """Создает файл с содержимым"""
    print(f"📄 Creating file: {path}")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"✅ Created: {path}")

def main():
    print("🚀 MORPHIK + COLPALI + MODAL АВТОМАТИЧЕСКАЯ НАСТРОЙКА")
    print("=" * 60)
    
    # 1. Клонируем morphik-core
    print("\n1️⃣ Cloning morphik-core...")
    if not os.path.exists("morphik-core"):
        run_command("git clone https://github.com/morphik-org/morphik-core.git")
    
    os.chdir("morphik-core")
    
    # 2. Создаем .env файл
    print("\n2️⃣ Creating .env file...")
    env_content = """# Morphik Configuration
JWT_SECRET_KEY="morphik-super-secret-key-2024"
POSTGRES_URI="postgresql+asyncpg://morphik:morphik@localhost:5432/morphik"

# Modal API Configuration
MORPHIK_EMBEDDING_API_KEY="your-modal-api-key"
MORPHIK_EMBEDDING_API_DOMAIN="https://your-username--morphik-colpali-serve.modal.run"

# Optional API Keys
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""
GEMINI_API_KEY=""

# Debug settings
LOG_LEVEL="DEBUG"
"""
    create_file(".env", env_content)
    
    # 3. Создаем правильный morphik.toml
    print("\n3️⃣ Creating morphik.toml...")
    morphik_toml = """[api]
host = "0.0.0.0"
port = 8000
reload = true

[auth]
jwt_algorithm = "HS256"
dev_mode = true
dev_entity_id = "dev_user"
dev_entity_type = "developer"
dev_permissions = ["read", "write", "admin"]

#### Registered models
[registered_models]
# OpenAI models
openai_gpt4-1 = { model_name = "gpt-4.1" }
openai_gpt4-1-mini = { model_name = "gpt-4.1-mini" }

# Anthropic models
claude_sonnet = { model_name = "claude-3-7-sonnet-latest" }

openai_embedding = { model_name = "text-embedding-3-small" }

#### Component configurations
[agent]
model = "openai_gpt4-1-mini"

[completion]
model = "openai_gpt4-1-mini"
default_max_tokens = "1000"
default_temperature = 0.3

[database]
provider = "postgres"
pool_size = 10
max_overflow = 15
pool_recycle = 3600
pool_timeout = 10
pool_pre_ping = true
max_retries = 3
retry_delay = 1.0

[embedding]
model = "openai_embedding"
dimensions = 1536
similarity_metric = "cosine"

[parser]
chunk_size = 6000
chunk_overlap = 300
use_unstructured_api = false
use_contextual_chunking = false

[reranker]
use_reranker = false

[storage]
provider = "local"
storage_path = "./storage"

[vector_store]
provider = "pgvector"

[multivector_store]
provider = "postgres"  # ВАЖНО: НЕ "morphik"!

[rules]
model = "openai_gpt4-1-mini"
batch_size = 4096

[morphik]
enable_colpali = true
mode = "self_hosted"
api_domain = "api.morphik.ai"
# КЛЮЧЕВАЯ НАСТРОЙКА: Ваш Modal API
morphik_embedding_api_domain = "https://your-username--morphik-colpali-serve.modal.run"
colpali_mode = "api"  # Используем внешний Modal API

[graph]
model = "openai_gpt4-1-mini"
enable_entity_resolution = true

[telemetry]
enabled = false
"""
    create_file("morphik.toml", morphik_toml)
    
    # 4. Создаем docker-compose.dev.yml
    print("\n4️⃣ Creating docker-compose.dev.yml...")
    docker_compose = """# Docker Compose для Morphik + ColPali + Modal
services:
  morphik:
    build: .
    ports:
      - "8000:8000"
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-morphik-super-secret-key-2024}
      - POSTGRES_URI=postgresql+asyncpg://morphik:morphik@postgres:5432/morphik
      - PGPASSWORD=morphik
      - LOG_LEVEL=DEBUG
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - MORPHIK_EMBEDDING_API_KEY=${MORPHIK_EMBEDDING_API_KEY}
      - MORPHIK_EMBEDDING_API_DOMAIN=${MORPHIK_EMBEDDING_API_DOMAIN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs
      - ./morphik.toml:/app/morphik.toml
      - huggingface_cache:/root/.cache/huggingface
      - ./core:/app/core
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - morphik-network
    env_file:
      - .env

  worker:
    build:
      context: .
      dockerfile: dockerfile
    command: arq core.workers.ingestion_worker.WorkerSettings
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-morphik-super-secret-key-2024}
      - POSTGRES_URI=postgresql+asyncpg://morphik:morphik@postgres:5432/morphik
      - PGPASSWORD=morphik
      - LOG_LEVEL=DEBUG
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - MORPHIK_EMBEDDING_API_KEY=${MORPHIK_EMBEDDING_API_KEY}
      - MORPHIK_EMBEDDING_API_DOMAIN=${MORPHIK_EMBEDDING_API_DOMAIN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs
      - ./morphik.toml:/app/morphik.toml
      - huggingface_cache:/root/.cache/huggingface
      - ./core:/app/core
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - morphik-network
    env_file:
      - .env

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - morphik-network

  postgres:
    image: pgvector/pgvector:pg16
    shm_size: 128mb
    environment:
      - POSTGRES_USER=morphik
      - POSTGRES_PASSWORD=morphik
      - POSTGRES_DB=morphik
      - PGDATA=/var/lib/postgresql/data/pgdata
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U morphik -d morphik"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - morphik-network

networks:
  morphik-network:
    driver: bridge

volumes:
  postgres_data:
  huggingface_cache:
  redis_data:
"""
    create_file("docker-compose.dev.yml", docker_compose)
    
    # 5. Создаем Modal API файл
    print("\n5️⃣ Creating Modal ColPali API...")
    modal_api = '''import io
import base64
import logging
from typing import List, Dict, Any
import numpy as np
import torch
from PIL import Image
import modal

# Modal configuration
app = modal.App("morphik-colpali")

colpali_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install([
        "torch==2.5.1",
        "transformers==4.51.3", 
        "pillow>=10.0.0",
        "numpy>=1.24.0",
        "colpali-engine@git+https://github.com/illuin-tech/colpali@80fb72c9b827ecdb5687a3a8197077d0d01791b3",
    ])
    .env({"TOKENIZERS_PARALLELISM": "false"})
)

model = None
processor = None
device = None

def load_model():
    """Загружает модель ColQwen2.5 БЕЗ max_length параметров!"""
    global model, processor, device
    
    if model is None:
        from colpali_engine.models import ColQwen2_5, ColQwen2_5_Processor
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🚀 Loading ColQwen2.5 model on {device}")
        
        # ВАЖНО: БЕЗ max_length и truncation параметров!
        processor = ColQwen2_5_Processor.from_pretrained(
            "tsystems/colqwen2.5-3b-multilingual-v1.0"
        )
        
        model = ColQwen2_5.from_pretrained(
            "tsystems/colqwen2.5-3b-multilingual-v1.0",
            torch_dtype=torch.bfloat16,
            device_map=device,
            attn_implementation="flash_attention_2" if device == "cuda" else "eager",
        ).eval()
        
        print("✅ ColQwen2.5 model loaded successfully!")
    
    return model, processor, device

def resize_image_if_needed(img: Image.Image, max_size: int = 1024) -> Image.Image:
    """Resize изображения для оптимизации"""
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        print(f"📏 Resized image to {img.size}")
    return img

def process_base64_images(base64_images: List[str]) -> List[Image.Image]:
    """Обрабатывает base64 изображения"""
    images = []
    for i, b64_img in enumerate(base64_images):
        try:
            if b64_img.startswith("data:"):
                b64_img = b64_img.split(",", 1)[1]
            
            img_bytes = base64.b64decode(b64_img)
            img = Image.open(io.BytesIO(img_bytes))
            
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            img = resize_image_if_needed(img)
            images.append(img)
            
            print(f"✅ Processed image {i+1}: {img.size}, mode: {img.mode}")
            
        except Exception as e:
            print(f"❌ Error processing image {i+1}: {e}")
            placeholder = Image.new("RGB", (224, 224), color=(128, 128, 128))
            images.append(placeholder)
    
    return images

def process_texts(texts: List[str]) -> List[str]:
    """Обрабатывает текстовые данные"""
    processed = []
    for i, text in enumerate(texts):
        if isinstance(text, str) and len(text.strip()) > 0:
            processed.append(text.strip())
        else:
            processed.append("")
        print(f"✅ Processed text {i+1}: {len(processed[-1])} chars")
    
    return processed

@app.function(
    image=colpali_image,
    gpu=modal.gpu.A100(count=1, size="40GB"),
    timeout=3600,
    container_idle_timeout=300,
    allow_concurrent_inputs=10,
)
def process_embeddings(input_type: str, inputs: List[str]) -> Dict[str, Any]:
    """Основная функция обработки embeddings"""
    model, processor, device = load_model()
    
    print(f"🔥 Processing {len(inputs)} {input_type} inputs")
    
    try:
        if input_type == "image":
            images = process_base64_images(inputs)
            
            with torch.no_grad():
                processed_images = processor.process_images(images).to(device)
                embeddings_tensor = model(**processed_images)
                embeddings_np = embeddings_tensor.cpu().float().numpy()
                
                print(f"✅ Generated {len(embeddings_np)} image embeddings")
                print(f"📊 Shape per embedding: {embeddings_np[0].shape}")
                
        elif input_type == "text":
            texts = process_texts(inputs)
            
            with torch.no_grad():
                processed_texts = processor.process_queries(texts).to(device)
                embeddings_tensor = model(**processed_texts)
                embeddings_np = embeddings_tensor.cpu().float().numpy()
                
                print(f"✅ Generated {len(embeddings_np)} text embeddings")
                print(f"📊 Shape per embedding: {embeddings_np[0].shape}")
                
        else:
            raise ValueError(f"Unsupported input_type: {input_type}")
        
        result = {
            "embeddings": [emb.tolist() for emb in embeddings_np],
            "input_type": input_type,
            "count": len(embeddings_np)
        }
        
        print(f"🎯 Successfully processed {result['count']} embeddings")
        return result
        
    except Exception as e:
        print(f"❌ Error in process_embeddings: {e}")
        raise

@app.function(image=colpali_image)
@modal.web_endpoint(method="POST", path="/embeddings")
def serve_embeddings(request_data: Dict[str, Any]) -> bytes:
    """HTTP endpoint для morphik-core - возвращает .npz формат"""
    try:
        input_type = request_data.get("input_type")
        inputs = request_data.get("inputs", [])
        
        if not input_type or not inputs:
            raise ValueError("Missing input_type or inputs")
        
        print(f"🌐 HTTP API: Processing {len(inputs)} {input_type} inputs")
        
        result = process_embeddings.remote(input_type, inputs)
        embeddings_data = result
        
        # Конвертируем в .npz формат для morphik-core
        buffer = io.BytesIO()
        
        embeddings_arrays = {}
        embeddings_arrays["count"] = np.array([embeddings_data["count"]])
        embeddings_arrays["input_type"] = np.array([embeddings_data["input_type"]], dtype='<U10')
        
        for i, embedding in enumerate(embeddings_data["embeddings"]):
            embeddings_arrays[f"emb_{i}"] = np.array(embedding)
        
        np.savez_compressed(buffer, **embeddings_arrays)
        buffer.seek(0)
        
        print(f"✅ HTTP API: Returning .npz with {embeddings_data['count']} embeddings")
        
        return buffer.getvalue()
        
    except Exception as e:
        print(f"❌ HTTP API Error: {e}")
        raise modal.web.HTTPException(status_code=500, detail=str(e))

@app.function(image=colpali_image)
def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    model, processor, device = load_model()
    return {
        "status": "healthy", 
        "device": device,
        "model_loaded": model is not None
    }

if __name__ == "__main__":
    with app.run():
        test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        result = process_embeddings.remote("image", [test_image_b64])
        print("Test result:", type(result), len(result.get("embeddings", [])))
'''
    create_file("modal_colpali_api.py", modal_api)
    
    # 6. Создаем debug патчи
    print("\n6️⃣ Creating debug patches...")
    debug_patches = '''#!/usr/bin/env python3
"""Добавляет debug логирование в morphik-core"""
import os
import re

def patch_colpali_client():
    """Добавляет логирование в colpali_api_embedding_model.py"""
    file_path = "core/embedding/colpali_api_embedding_model.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Добавляем логирование если его еще нет
    if "🚀 Calling Modal API" not in content:
        # Ищем метод call_api и добавляем логирование
        lines = content.split('\\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # После timeout добавляем логирование запроса
            if "timeout = Timeout(" in line:
                new_lines.append("")
                new_lines.append('        # DEBUG: Добавлено логирование')
                new_lines.append('        logger.info(f"🚀 Calling Modal API: {self.endpoint}")')
                new_lines.append('        logger.info(f"📤 Payload: input_type={input_type}, inputs_count={len(inputs)}")')
            
            # После resp.raise_for_status() добавляем логирование ответа
            if "resp.raise_for_status()" in line:
                new_lines.append("")
                new_lines.append('        # DEBUG: Логирование ответа')
                new_lines.append('        logger.info(f"📥 Response status: {resp.status_code}")')
                new_lines.append('        logger.info(f"📥 Response size: {len(resp.content)} bytes")')
        
        # Сохраняем изменения
        with open(file_path, 'w') as f:
            f.write('\\n'.join(new_lines))
        
        print(f"✅ Added debug logging to {file_path}")
    else:
        print(f"ℹ️ Debug logging already present in {file_path}")

if __name__ == "__main__":
    print("🔧 Applying debug patches...")
    patch_colpali_client()
    print("✅ Debug patches applied!")
'''
    create_file("apply_debug_patches.py", debug_patches)
    
    # 7. Создаем тесты
    print("\n7️⃣ Creating test files...")
    test_file = '''import asyncio
import sys
from morphik import Morphik

async def test_morphik_colpali():
    """Тест интеграции Morphik + ColPali + Modal"""
    try:
        print("🚀 Testing Morphik + ColPali integration...")
        
        db = Morphik("http://localhost:8000", is_local=True)
        
        # 1. Тест обычных embeddings
        print("1️⃣ Testing regular embeddings...")
        doc1 = await db.ingest_text(
            content="Regular document without ColPali", 
            use_colpali=False,
            filename="regular.txt"
        )
        print(f"✅ Regular document: {doc1.external_id}")
        
        # 2. Тест ColPali embeddings
        print("2️⃣ Testing ColPali embeddings...")
        doc2 = await db.ingest_text(
            content="ColPali document for multimodal processing", 
            use_colpali=True,
            filename="colpali.txt"
        )
        print(f"✅ ColPali document: {doc2.external_id}")
        
        # 3. Тест поиска
        print("3️⃣ Testing search...")
        chunks = await db.retrieve_chunks("multimodal processing", use_colpali=True, k=2)
        print(f"✅ ColPali search: {len(chunks)} chunks found")
        
        # 4. Тест запроса
        print("4️⃣ Testing query...")
        response = await db.query("What is this about?", use_colpali=True, k=2)
        print(f"✅ Generated response: {len(response.completion)} chars")
        
        print("\\n🎉 ALL TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_morphik_colpali())
    sys.exit(0 if success else 1)
'''
    create_file("test_colpali_integration.py", test_file)
    
    # 8. Создаем скрипт запуска
    print("\n8️⃣ Creating startup script...")
    startup_script = '''#!/bin/bash
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
'''
    create_file("start_morphik_colpali.sh", startup_script)
    run_command("chmod +x start_morphik_colpali.sh")
    
    # 9. Создаем README
    print("\n9️⃣ Creating README...")
    readme = '''# Morphik + ColPali + Modal Integration

Полная настройка Morphik Core с ColPali через Modal API.

## 🚀 Быстрый старт

1. **Настройте переменные окружения в .env:**
   ```bash
   # Добавьте ваши API ключи:
   OPENAI_API_KEY="sk-..."
   MORPHIK_EMBEDDING_API_KEY="your-modal-key"
   MORPHIK_EMBEDDING_API_DOMAIN="https://your-username--morphik-colpali-serve.modal.run"
   ```

2. **Запустите систему:**
   ```bash
   ./start_morphik_colpali.sh
   ```

3. **Деплойте Modal API:**
   ```bash
   # Установите modal
   pip install modal
   
   # Авторизуйтесь
   modal auth new
   
   # Деплойте API
   modal deploy modal_colpali_api.py
   
   # Получите URL и обновите .env
   ```

4. **Запустите тесты:**
   ```bash
   python test_colpali_integration.py
   ```

## 📊 Мониторинг

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

## 🔧 Отладка

```bash
# Логи Morphik
docker-compose -f docker-compose.dev.yml logs -f morphik

# Логи Worker
docker-compose -f docker-compose.dev.yml logs -f worker

# Логи PostgreSQL
docker-compose -f docker-compose.dev.yml logs -f postgres

# Modal логи
modal logs morphik-colpali
```

## 🛠️ Архитектура

- **Morphik Core** (Docker) - основная система с PostgreSQL + pgvector
- **Modal ColPali API** - GPU обработка embeddings
- **Правильная интеграция** через .npz формат

## 🎯 Ключевые настройки

- `multivector_store.provider = "postgres"`
- `colpali_mode = "api"`
- `morphik_embedding_api_domain` - ваш Modal URL
- Modal API возвращает .npz формат
- ColQwen2.5 БЕЗ max_length параметров
'''
    create_file("README_COLPALI.md", readme)
    
    print("\n" + "=" * 60)
    print("🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
    print("=" * 60)
    print("\n📋 Созданные файлы:")
    print("✅ .env - переменные окружения")
    print("✅ morphik.toml - конфигурация Morphik")
    print("✅ docker-compose.dev.yml - Docker настройка")
    print("✅ modal_colpali_api.py - Modal API код")
    print("✅ apply_debug_patches.py - debug патчи")
    print("✅ test_colpali_integration.py - тесты")
    print("✅ start_morphik_colpali.sh - скрипт запуска")
    print("✅ README_COLPALI.md - документация")
    
    print("\n🚀 СЛЕДУЮЩИЕ ШАГИ:")
    print("1️⃣ Добавьте ваши API ключи в .env файл")
    print("2️⃣ Запустите: ./start_morphik_colpali.sh")
    print("3️⃣ Деплойте Modal: modal deploy modal_colpali_api.py") 
    print("4️⃣ Обновите MORPHIK_EMBEDDING_API_DOMAIN в .env")
    print("5️⃣ Тестируйте: python test_colpali_integration.py")
    
    print(f"\n📂 Проект готов в: {os.getcwd()}")
    print("🎯 Все должно работать правильно!")

if __name__ == "__main__":
    main()