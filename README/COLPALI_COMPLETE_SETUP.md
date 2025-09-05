# ColPali Complete Setup Guide - Morphik Integration
## Полное руководство по настройке ColPali с нуля

### 📅 Дата исправления: 05.09.2025
### ⏱️ Время работы: ~8 часов
### 🎯 Результат: ColPali полностью работает, PDF отображаются как изображения

---

## 🔴 ПРОБЛЕМА: Почему ColPali не работал?

### Главная проблема:
**PDF страницы отображались как текстовые пути к файлам вместо изображений в UI чата**

### Цепочка проблем:
1. JWT токены не содержали `app_id` → API ключи не загружались
2. SQL запросы падали с ошибкой "app_id parameter not defined"
3. ColPali создавал правильные base64 изображения, НО:
   - Система сохраняла их в S3/MinIO
   - В базе данных сохранялись только пути типа `morphik_app/doc_id/0.png`
   - UI получал пути вместо изображений и не мог их отобразить

---

## 📊 ЧТО МЫ ДЕЛАЛИ (Хронология)

### 1. **Начало: Анализ проблемы** (2 часа)
```bash
# Проверяли логи
docker logs worker_v2
docker logs morphik_v2

# Обнаружили:
- "app_id parameter not defined" 
- API keys not showing in UI
- ColPali вроде работает, но изображения не показываются
```

### 2. **Первая попытка: Пересборка Docker** (30 минут)
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```
**Результат:** Не помогло, проблема в коде, не в сборке

### 3. **Скачивание и анализ официального Morphik** (1 час)
```bash
# Анализировали официальный репозиторий
https://github.com/morphik-org/morphik-core

# Сравнивали файлы:
- core/vector_store/multi_vector_store.py
- core/services/document_service.py
- core/auth_utils.py
```

### 4. **Исправление файлов** (3 часа)
Вместо пересборки начали копировать файлы напрямую:
```bash
# Быстрое применение изменений без пересборки
docker cp file.py container:/app/path/
docker restart container
```

### 5. **Очистка старых данных** (30 минут)
```sql
DELETE FROM multi_vector_embeddings;
DELETE FROM documents;
-- Удаляли данные с неправильным форматом
```

### 6. **Финальное тестирование** (1 час)
- Загрузка нового PDF
- Проверка формата хранения
- Тестирование поиска

---

## 🛠️ ВСЕ ИСПРАВЛЕННЫЕ ФАЙЛЫ

### 1. `/core/routes/auth.py`
**Проблема:** JWT токен не содержал app_id  
**Строка:** ~155  
```python
def create_access_token(user_id: str, username: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "entity_id": user_id,
        "entity_type": "user",
        "user_id": user_id,
        "username": username,
        "app_id": "morphik_app",  # ← КРИТИЧЕСКИ ВАЖНО!
        "permissions": ["read", "write"],
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

### 2. `/core/database/postgres_database.py`
**Проблема:** SQL параметр app_id не определялся правильно  
**Строка:** ~1035  
```python
def _build_access_filter_optimized(self, auth: AuthContext) -> str:
    """Build SQL filter based on auth context."""
    if auth.app_id:
        # Если есть app_id, используем только его
        return "app_id = :app_id"
    
    # Иначе используем сложную логику с user_id
    base_clauses = []
    if auth.entity_type == EntityType.USER:
        base_clauses.extend([
            "owner_id = :user_id AND owner_type = 'user'",
            ":user_id = ANY(readers)",
            ":user_id = ANY(writers)",
            ":user_id = ANY(admins)",
        ])
    # ...остальная логика
```

### 3. `/core/vector_store/multi_vector_store.py` 
**САМОЕ ВАЖНОЕ ИСПРАВЛЕНИЕ!**  
**Проблема:** ColPali изображения сохранялись в S3 как файлы  

#### Исправление А - Метод store_embeddings (строки 499-526):
```python
async def store_embeddings(self, chunks: List[DocumentChunk], app_id: Optional[str] = None):
    rows = []
    for chunk in chunks:
        # ... подготовка embeddings ...
        
        # КРИТИЧЕСКАЯ ЛОГИКА:
        content_to_store = chunk.content
        
        # Проверяем является ли это ColPali изображением
        is_colpali_image = False
        if chunk.metadata:
            is_colpali_image = chunk.metadata.get("is_image", False)
        
        # ColPali изображения НЕ ИДУТ В S3!
        if self.enable_external_storage and self.storage and not is_colpali_image:
            # Только обычный текст сохраняем в S3
            storage_key = await self._store_content_externally(
                chunk.content, chunk.document_id, chunk.chunk_number, 
                json.dumps(chunk.metadata), app_id
            )
            if storage_key:
                content_to_store = storage_key  # Сохраняем путь
        elif is_colpali_image:
            # ColPali изображения остаются как base64 в БД!
            logger.debug(f"Storing ColPali image directly in database")
            # content_to_store остается как chunk.content (base64)
        
        rows.append((
            chunk.document_id,
            chunk.chunk_number, 
            content_to_store,  # base64 для изображений, путь для текста
            json.dumps(chunk.metadata),  # НЕ str()!
            binary_embeddings
        ))
```

#### Исправление Б - Метод _retrieve_content_from_storage (строки 450-456):
```python
async def _retrieve_content_from_storage(self, storage_key: str, chunk_metadata: Optional[str]) -> str:
    # ... загрузка из S3 ...
    
    if chunk_metadata:
        metadata = json.loads(chunk_metadata)
        is_image = metadata.get("is_image", False)
        
        if is_image:
            # Для изображений возвращаем с data URI префиксом
            base64_content = base64.b64encode(content_bytes).decode("utf-8")
            result = f"data:image/png;base64,{base64_content}"  # ← ВАЖНО!
            return result
        else:
            # Для текста просто декодируем
            return content_bytes.decode("utf-8")
```

### 4. `/core/utils/performance_tracker.py`
**Проблема:** Несоответствие сигнатур методов  
**Строка:** ~42  
```python
def track_operation(self, operation: str, duration: float, metadata: Optional[Dict] = None):
    # Добавлен третий параметр metadata
    self.operations.append({
        "operation": operation,
        "duration": duration,
        "metadata": metadata or {}
    })
```

### 5. `/core/auth_utils.py`
**Проблема:** В dev_mode использовались фейковые ID  
**Строка:** ~29-37  
```python
if settings.dev_mode:
    return AuthContext(
        entity_type=EntityType(settings.dev_entity_type),
        entity_id="8",  # Реальный ID пользователя из БД!
        permissions=set(settings.dev_permissions),
        user_id="8",    # Реальный ID, не "dev_user"!
        app_id="morphik_app",
    )
```

### 6. Все места с метаданными
**Проблема:** Использовался `str(metadata)` вместо `json.dumps(metadata)`  
**Файлы:**
- `/core/vector_store/multi_vector_store.py`
- `/core/vector_store/fast_multivector_store.py`

```python
# Было:
str(chunk.metadata)  # Создает Python repr: "{'is_image': True}"

# Стало:
json.dumps(chunk.metadata)  # Создает JSON: '{"is_image": true}'
```

---

## 🚀 НАСТРОЙКА С НУЛЯ (Для программистов)

### Шаг 1: Окружение
```bash
# .env файл
MORPHIK_EMBEDDING_API_KEY=dummy_key_for_modal
MORPHIK_EMBEDDING_API_DOMAIN=https://rugusev--colpali-morphik-official-fastapi-app.modal.run
MULTIVECTOR_STORE_PROVIDER=postgres  # НЕ turbopuffer!
STORAGE_PROVIDER=aws-s3
DATABASE_URL=postgresql://morphik:morphik@135.181.106.12:5432/morphik
```

### Шаг 2: Применить все исправления
1. Скопировать все исправления из раздела выше
2. Особое внимание на `/core/vector_store/multi_vector_store.py`

### Шаг 3: База данных
```sql
-- Проверить структуру таблицы
CREATE TABLE IF NOT EXISTS multi_vector_embeddings (
    id BIGSERIAL PRIMARY KEY,
    document_id TEXT NOT NULL,
    chunk_number INTEGER NOT NULL,
    content TEXT NOT NULL,  -- Здесь хранится base64, НЕ путь!
    chunk_metadata TEXT,    -- JSON с {"is_image": true}
    embeddings BIT(128)[]
);
```

### Шаг 4: Запуск без пересборки
```bash
# Если уже есть контейнеры, просто копируем файлы
docker cp core/vector_store/multi_vector_store.py worker_v2:/app/core/vector_store/
docker cp core/routes/auth.py morphik_v2:/app/core/routes/
docker cp core/database/postgres_database.py morphik_v2:/app/core/database/
docker cp core/auth_utils.py morphik_v2:/app/core/

# Перезапускаем
docker restart worker_v2 morphik_v2
```

### Шаг 5: Проверка работы
```python
# Проверочный скрипт
import psycopg2
conn = psycopg2.connect('postgresql://morphik:morphik@135.181.106.12:5432/morphik')
cur = conn.cursor()

# После загрузки PDF проверить:
cur.execute("""
    SELECT 
        chunk_number,
        CASE 
            WHEN content LIKE 'data:image%' THEN '✅ OK - Base64 image'
            WHEN content LIKE '%/%' AND LENGTH(content) < 200 THEN '❌ FAIL - File path'
            ELSE '? Unknown'
        END as status
    FROM multi_vector_embeddings
""")

for row in cur.fetchall():
    print(f"Chunk {row[0]}: {row[1]}")

# Ожидаемый результат: все chunks должны быть "✅ OK - Base64 image"
```

---

## 📋 ЧЕКЛИСТ ДИАГНОСТИКИ

### ✅ Правильная работа:
- [ ] JWT токены содержат `app_id: "morphik_app"`
- [ ] API ключи видны в UI настройках
- [ ] PDF конвертируется в изображения
- [ ] В БД хранятся base64 строки начинающиеся с `data:image/png;base64,`
- [ ] UI отображает страницы PDF как изображения
- [ ] Поиск находит контент в PDF

### ❌ Признаки проблем:
- JWT токен без app_id → API ключи не загружаются
- В БД пути типа `morphik_app/xxx/0.png` → неправильное хранение
- UI показывает текст вместо изображений → не добавлен data URI префикс
- Ошибка "app_id parameter not defined" → проблема в postgres_database.py

---

## 🏗️ АРХИТЕКТУРА COLPALI В MORPHIK

```
┌─────────────┐
│   PDF File  │
└──────┬──────┘
       ↓
┌─────────────────────────────────┐
│         Worker Process          │
│  1. PyMuPDF/pdf2image → PIL     │
│  2. PIL → base64 с префиксом    │
│  3. Отправка на ColPali API     │
└──────┬──────────────────────────┘
       ↓
┌─────────────────────────────────┐
│      ColPali Modal API          │
│  Создание multi-vector          │
│  embeddings для изображений     │
└──────┬──────────────────────────┘
       ↓
┌─────────────────────────────────┐
│         PostgreSQL              │
│  Таблица: multi_vector_embeddings│
│  ┌─────────────────────────┐    │
│  │ content: data:image/... │    │ ← КРИТИЧНО!
│  │ metadata: {"is_image":true}  │
│  │ embeddings: bit vectors │    │
│  └─────────────────────────┘    │
└──────┬──────────────────────────┘
       ↓
┌─────────────────────────────────┐
│      Поиск (Query)              │
│  1. Текст → ColPali embedding   │
│  2. max_sim similarity search   │
│  3. Возврат base64 изображений  │
└──────┬──────────────────────────┘
       ↓
┌─────────────┐
│     UI      │
│  Отображение│
│  изображений│
└─────────────┘
```

---

## ⚠️ КРИТИЧЕСКИЕ МОМЕНТЫ

1. **НИКОГДА** не сохраняйте ColPali изображения в S3
2. **ВСЕГДА** используйте `postgres` для MULTIVECTOR_STORE_PROVIDER
3. **ОБЯЗАТЕЛЬНО** добавляйте `app_id` в JWT токены
4. **ПРОВЕРЯЙТЕ** что content начинается с `data:image/png;base64,`
5. **НЕ ЗАБЫВАЙТЕ** про json.dumps() для метаданных

---

## 📈 МЕТРИКИ УСПЕХА

- **Размер base64 на страницу:** ~500KB
- **Время обработки PDF:** ~2 минуты на 16 страниц
- **Время поиска:** ~1-2 секунды
- **LLM ответ:** ~15 секунд (Claude 3 Opus)

---

## 🆘 ЭКСТРЕННОЕ ВОССТАНОВЛЕНИЕ

Если что-то сломалось:
```bash
# 1. Очистить данные
psql -d morphik -c "TRUNCATE multi_vector_embeddings, documents CASCADE;"

# 2. Применить все исправления из этого файла

# 3. Перезапустить контейнеры
docker restart worker_v2 morphik_v2

# 4. Загрузить тестовый PDF и проверить формат хранения
```

---

*Документ создан: 05.09.2025*
*Статус: ✅ ПОЛНОСТЬЮ РАБОТАЕТ*