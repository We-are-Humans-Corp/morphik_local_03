#!/usr/bin/env python3
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
        lines = content.split('\n')
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
            f.write('\n'.join(new_lines))
        
        print(f"✅ Added debug logging to {file_path}")
    else:
        print(f"ℹ️ Debug logging already present in {file_path}")

if __name__ == "__main__":
    print("🔧 Applying debug patches...")
    patch_colpali_client()
    print("✅ Debug patches applied!")
