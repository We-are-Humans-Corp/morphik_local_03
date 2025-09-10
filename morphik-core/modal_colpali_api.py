import io
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
