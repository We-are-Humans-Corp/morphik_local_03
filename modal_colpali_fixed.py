# modal_colpali_fixed.py - ПРАВИЛЬНЫЙ ФОРМАТ NPZ
import modal
import numpy as np
import io
from fastapi import FastAPI, Response
import base64
from PIL import Image
import torch
import time

app = modal.App("morphik-processor")

# Правильный образ с зависимостями
colpali_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(["git"])  # Нужен для установки colpali-engine из GitHub
    .pip_install([
        "torch==2.5.1",
        "transformers==4.51.3", 
        "pillow>=10.0.0",
        "numpy>=1.24.0",
        "colpali-engine@git+https://github.com/illuin-tech/colpali@80fb72c9b827ecdb5687a3a8197077d0d01791b3",
        "fastapi",
    ])
    .env({"TOKENIZERS_PARALLELISM": "false"})
)

@app.function(
    image=colpali_image,
    gpu="A100-40GB",  # Современный формат
    timeout=3600,
    scaledown_window=300,  # Современный стандарт вместо container_idle_timeout
)
def process_colpali():
    """Основная функция обработки ColPali"""
    from colpali_engine.models import ColQwen2_5, ColQwen2_5_Processor
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🚀 Loading ColQwen2.5 model on {device}")
    
    # БЕЗ max_length параметров!
    processor = ColQwen2_5_Processor.from_pretrained(
        "tsystems/colqwen2.5-3b-multilingual-v1.0"
    )
    
    model = ColQwen2_5.from_pretrained(
        "tsystems/colqwen2.5-3b-multilingual-v1.0",
        torch_dtype=torch.bfloat16,
        device_map=device,
    ).eval()
    
    print("✅ ColQwen2.5 model loaded successfully!")
    
    web_app = FastAPI()
    
    @web_app.get("/health")
    def health():
        return {"status": "healthy", "device": device}
    
    @web_app.post("/embeddings")
    async def embeddings_endpoint(data: dict) -> Response:
        """КРИТИЧНО: Возвращает NPZ формат!"""
        input_type = data.get("input_type")
        inputs = data.get("inputs", [])
        
        print(f"📥 Processing {len(inputs)} {input_type} inputs")
        embeddings_list = []
        
        try:
            if input_type == "image":
                # Обработка изображений
                images = []
                for b64_img in inputs:
                    if b64_img.startswith("data:"):
                        b64_img = b64_img.split(",", 1)[1]
                    
                    img_bytes = base64.b64decode(b64_img)
                    img = Image.open(io.BytesIO(img_bytes))
                    
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    
                    # Resize если слишком большое
                    if max(img.size) > 1024:
                        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                    
                    images.append(img)
                
                # ColPali обработка БЕЗ дополнительных параметров
                with torch.no_grad():
                    processed = processor.process_images(images).to(device)
                    embeddings_tensor = model(**processed)
                    embeddings_np = embeddings_tensor.cpu().float().numpy()
                    
                for emb in embeddings_np:
                    embeddings_list.append(emb.tolist())
                    
            elif input_type == "text":
                # Обработка текстов
                with torch.no_grad():
                    processed = processor.process_queries(inputs).to(device)
                    embeddings_tensor = model(**processed)
                    embeddings_np = embeddings_tensor.cpu().float().numpy()
                    
                for emb in embeddings_np:
                    embeddings_list.append(emb.tolist())
                    
            else:
                raise ValueError(f"Unsupported input_type: {input_type}")
            
            # ГЛАВНОЕ: Возвращаем NPZ формат!
            buffer = io.BytesIO()
            
            embeddings_arrays = {}
            embeddings_arrays["count"] = np.array([len(embeddings_list)])
            embeddings_arrays["input_type"] = np.array([input_type], dtype='<U10')
            
            for i, embedding in enumerate(embeddings_list):
                embeddings_arrays[f"emb_{i}"] = np.array(embedding)
            
            np.savez_compressed(buffer, **embeddings_arrays)
            buffer.seek(0)
            
            print(f"✅ Returning NPZ with {len(embeddings_list)} embeddings")
            
            return Response(
                content=buffer.getvalue(),
                media_type="application/octet-stream"  # НЕ JSON!
            )
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    return web_app

if __name__ == "__main__":
    print("🚀 Deploy command: modal deploy modal_colpali_fixed.py")
    print("📝 After deployment, update the URL in .env and morphik.toml")