"""
ColPali Modal Deployment с оптимизацией для быстрой работы
Улучшения:
1. container_idle_timeout=300 - держит контейнер 5 минут после запроса
2. Оптимизированная загрузка модели
3. Кеширование в памяти
"""

import modal
import numpy as np
from typing import List
import io
import time

app = modal.App("colpali-morphik-official")

# Образ с зависимостями
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch==2.1.2",
    "transformers==4.40.0", 
    "pillow",
    "colpali-engine==0.3.2",
    "numpy",
    "fastapi",
)

# Хранилище для модели (чтобы не скачивать каждый раз)
model_volume = modal.Volume.from_name("colpali-model-cache", create_if_missing=True)

@app.cls(
    image=image,
    gpu="A100",  # или "A10G" для экономии
    container_idle_timeout=300,  # ← КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: держим 5 минут!
    volumes={"/model_cache": model_volume},
    concurrency_limit=10,  # До 10 параллельных запросов
    allow_concurrent_inputs=True,
    memory=32768,  # 32GB RAM
)
class ColPaliModel:
    def __init__(self):
        import torch
        from colpali_engine.models import ColPali, ColPaliProcessor
        
        print("🚀 Инициализация ColPali модели...")
        start = time.time()
        
        # Проверяем кеш модели
        model_path = "/model_cache/colpali"
        
        try:
            # Пытаемся загрузить из кеша
            self.model = ColPali.from_pretrained(
                model_path, 
                torch_dtype=torch.bfloat16,
                device_map="cuda"
            )
            self.processor = ColPaliProcessor.from_pretrained(model_path)
            print(f"✅ Модель загружена из кеша за {time.time() - start:.2f}с")
        except:
            # Первый раз - скачиваем и сохраняем
            print("📥 Скачивание модели (первый запуск)...")
            self.model = ColPali.from_pretrained(
                "vidore/colpali-v1.2",
                torch_dtype=torch.bfloat16,
                device_map="cuda"
            )
            self.processor = ColPaliProcessor.from_pretrained("vidore/colpali-v1.2")
            
            # Сохраняем в volume для следующих запусков
            self.model.save_pretrained(model_path)
            self.processor.save_pretrained(model_path)
            print(f"✅ Модель загружена и сохранена за {time.time() - start:.2f}с")
        
        self.model.eval()
        print("✨ ColPali готов к работе!")
    
    @modal.method()
    def embed_batch(self, contents: List[bytes], content_types: List[str], batch_size: int = 8):
        """
        Обрабатывает батч изображений/текстов
        """
        import torch
        from PIL import Image
        import io
        
        embeddings = []
        
        # Обрабатываем батчами для оптимизации GPU
        for i in range(0, len(contents), batch_size):
            batch_contents = contents[i:i+batch_size]
            batch_types = content_types[i:i+batch_size]
            
            batch_inputs = []
            for content, ctype in zip(batch_contents, batch_types):
                if ctype == "image":
                    # Декодируем base64 изображение
                    import base64
                    img_bytes = base64.b64decode(content)
                    img = Image.open(io.BytesIO(img_bytes))
                    batch_inputs.append(img)
                else:
                    # Текст обрабатываем как есть
                    batch_inputs.append(content)
            
            # Обработка через ColPali
            with torch.no_grad():
                inputs = self.processor(batch_inputs, return_tensors="pt").to("cuda")
                outputs = self.model(**inputs)
                
                # Конвертируем в список для каждого элемента
                for j in range(len(batch_inputs)):
                    emb = outputs.last_hidden_state[j].cpu().numpy()
                    embeddings.append(emb)
        
        return embeddings

@app.function(
    image=image,
    container_idle_timeout=300,  # Для FastAPI endpoint тоже!
    concurrency_limit=100,
)
def fastapi_app():
    """
    FastAPI endpoint для совместимости с текущим API
    """
    from fastapi import FastAPI, Response
    import numpy as np
    import io
    
    web_app = FastAPI()
    model = ColPaliModel()
    
    @web_app.get("/health")
    def health_check():
        return {
            "status": "healthy",
            "service": "colpali",
            "model_loaded": True,
            "container_idle_timeout": 300,
            "optimization": "enabled"
        }
    
    @web_app.post("/embeddings")
    async def create_embeddings(data: dict) -> Response:
        """
        Совместимый endpoint с текущим API
        Возвращает NPZ файл с эмбеддингами
        """
        input_type = data.get("input_type", "image")
        inputs = data.get("inputs", [])
        
        # Подготавливаем типы контента
        content_types = [input_type] * len(inputs)
        
        # Получаем эмбеддинги
        embeddings = model.embed_batch.remote(inputs, content_types)
        
        # Упаковываем в NPZ формат
        npz_buffer = io.BytesIO()
        np_data = {
            'count': len(embeddings),
        }
        for i, emb in enumerate(embeddings):
            np_data[f'emb_{i}'] = np.array(emb)
        
        np.savez_compressed(npz_buffer, **np_data)
        npz_buffer.seek(0)
        
        return Response(
            content=npz_buffer.read(),
            media_type="application/octet-stream"
        )
    
    return web_app

if __name__ == "__main__":
    # Для локального тестирования
    print("🚀 Деплой на Modal...")
    print("Используйте: modal deploy colpali_modal_optimized.py")
    print("Endpoint будет: https://<your-username>--colpali-morphik-official-fastapi-app.modal.run")