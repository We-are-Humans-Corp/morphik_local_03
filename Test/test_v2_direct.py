#!/usr/bin/env python3
"""
Тест производительности ColPali V2 на Modal
Сравнение с V1 для PDF документа
"""

import base64
import time
import requests
import json
from PIL import Image
import fitz  # PyMuPDF
import io

def pdf_to_images(pdf_path, max_pages=3):
    """Конвертирует первые N страниц PDF в изображения"""
    doc = fitz.open(pdf_path)
    images = []
    
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        
        # Рендерим страницу в изображение
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # 2x масштаб для качества
        img_data = pix.pil_tobytes(format="PNG")
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        images.append(img_base64)
    
    doc.close()
    return images

def test_endpoint(url, name, images):
    """Тестирует endpoint с изображениями"""
    print(f"\n{'='*50}")
    print(f"Тестирование {name}")
    print(f"URL: {url}")
    print(f"{'='*50}")
    
    # Подготовка данных
    payload = {
        "input_type": "image",
        "inputs": images
    }
    
    # Первый запрос (может быть холодный старт)
    print("\n1️⃣  Первый запрос (возможен холодный старт)...")
    start = time.time()
    
    try:
        response = requests.post(
            f"{url}/embeddings",
            json=payload,
            timeout=300  # 5 минут таймаут
        )
        
        first_time = time.time() - start
        
        if response.status_code == 200:
            print(f"✅ Успешно за {first_time:.2f} секунд")
            print(f"   Размер ответа: {len(response.content) / 1024:.2f} KB")
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
            return
            
    except requests.exceptions.Timeout:
        print(f"⏱️  Таймаут после 300 секунд")
        return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return
    
    # Второй запрос (должен быть быстрее для V2)
    print("\n2️⃣  Второй запрос (контейнер должен быть горячим)...")
    start = time.time()
    
    try:
        response = requests.post(
            f"{url}/embeddings",
            json=payload,
            timeout=300
        )
        
        second_time = time.time() - start
        
        if response.status_code == 200:
            print(f"✅ Успешно за {second_time:.2f} секунд")
            
            # Анализ улучшения
            if first_time > 0:
                speedup = first_time / second_time
                print(f"\n📊 Ускорение: {speedup:.1f}x")
                print(f"   Экономия времени: {first_time - second_time:.2f} секунд")
        else:
            print(f"❌ Ошибка {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    return {
        "first_request": first_time,
        "second_request": second_time if 'second_time' in locals() else None
    }

def main():
    pdf_path = "/Users/fedor/Documents/Botler - July 2025 .pdf"
    
    print("🚀 Тест производительности ColPali на Modal")
    print(f"📄 Документ: {pdf_path}")
    
    # Конвертируем PDF в изображения
    print("\n📸 Конвертация PDF в изображения...")
    images = pdf_to_images(pdf_path, max_pages=3)
    print(f"✅ Конвертировано {len(images)} страниц")
    
    # URL для тестирования
    v1_url = "https://rugusev--colpali-morphik-official-fastapi-app.modal.run"
    v2_url = "https://rugusev--colpali-morphik-v2-fastapi-app.modal.run"
    
    # Тест V1
    v1_results = test_endpoint(v1_url, "ColPali V1 (оригинал)", images)
    
    # Небольшая пауза между тестами
    print("\n⏳ Пауза 5 секунд...")
    time.sleep(5)
    
    # Тест V2
    v2_results = test_endpoint(v2_url, "ColPali V2 (оптимизированная)", images)
    
    # Итоговое сравнение
    print(f"\n{'='*50}")
    print("📊 ИТОГОВОЕ СРАВНЕНИЕ")
    print(f"{'='*50}")
    
    if v1_results and v2_results:
        print(f"\nV1 первый запрос:  {v1_results['first_request']:.2f}с")
        print(f"V2 первый запрос:  {v2_results['first_request']:.2f}с")
        
        if v1_results['second_request'] and v2_results['second_request']:
            print(f"\nV1 второй запрос:  {v1_results['second_request']:.2f}с")
            print(f"V2 второй запрос:  {v2_results['second_request']:.2f}с")
            
            v2_advantage = v1_results['second_request'] / v2_results['second_request']
            print(f"\n🎯 V2 быстрее V1 в {v2_advantage:.1f} раз на горячем контейнере!")

if __name__ == "__main__":
    main()