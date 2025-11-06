# Исправления и улучшения модулей БД

## Дата: 2025-11-06

### ✅ Исправленные проблемы

#### 1. SQLAlchemy: конфликт имени колонки `metadata`

**Проблема:**
```python
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved 
when using the Declarative API.
```

**Решение:**
- Переименовали колонку с `metadata` на `product_metadata`
- Обновили все файлы:
  - `app/db/postgres.py`
  - `app/db/README.md`
  - `DATABASE_SETUP.md`
  - `DATABASE_MODULES_SUMMARY.md`
  - `DATABASES_README.md`
  - `examples/database_usage_example.py`
  - `tests/test_database_modules.py`

**Использование:**
```python
product = await create_product(session, {
    "external_id": "prod_001",
    "title": "Product Name",
    "product_metadata": {"color": "red"}  # ← Новое имя поля
})
```

#### 2. Неправильное использование `get_session()`

**Проблема:**
```python
async for session in get_session():  # ❌ Ошибка!
    # TypeError: 'async for' requires an object with __aiter__ method
```

**Решение:**
```python
async with get_session() as session:  # ✅ Правильно!
    product = await create_product(session, {...})
```

`get_session()` возвращает async context manager, а не async iterator.

#### 3. Qdrant: требование UUID для ID точек

**Проблема:**
```
Unexpected Response: 400 (Bad Request)
Error: value test_vector_001 is not a valid point ID, 
valid values are either an unsigned integer or a UUID
```

**Решение:**
Добавили автоматическое преобразование строковых ID в UUID:

```python
from uuid import uuid5, NAMESPACE_DNS

def _product_id_to_uuid(product_id: str) -> str:
    """Convert product_id string to UUID string."""
    return str(uuid5(NAMESPACE_DNS, product_id))
```

**Преимущества:**
- ✅ Стабильные UUID для одинаковых product_id
- ✅ Прозрачно для пользователя (можно использовать строковые ID)
- ✅ Результаты поиска возвращают оригинальные product_id

**Использование:**
```python
# Добавление векторов
await manager.upsert_vectors(
    product_ids=["prod_001", "prod_002"],  # Строковые ID
    vectors=[vector1, vector2],
    payloads=[{"title": "Product 1"}, {"title": "Product 2"}]
)
# Внутри автоматически конвертируются в UUID

# Поиск
results = await manager.search_similar(query_vector, top_k=10)
# results[0]["id"] == "prod_001"  ← Возвращается оригинальный ID
```

### 📊 Измененные файлы

#### Код:
1. `app/db/postgres.py` - переименована колонка `metadata` → `product_metadata`
2. `app/db/qdrant.py` - добавлена функция `_product_id_to_uuid()` и автоматическая конвертация ID
3. `test_db_stage2.py` - исправлено использование `get_session()`
4. `examples/database_usage_example.py` - обновлены все примеры
5. `tests/test_database_modules.py` - обновлены тесты

#### Документация:
1. `app/db/README.md` - обновлены примеры и добавлено примечание о UUID
2. `DATABASE_SETUP.md` - обновлена SQL схема и примеры
3. `DATABASE_MODULES_SUMMARY.md` - обновлена спецификация модели
4. `DATABASES_README.md` - обновлены все примеры использования

### ✅ Результаты тестирования

Все тесты успешно пройдены:

```
==================================================
  ТЕСТИРОВАНИЕ ЭТАПА 2: Базы данных
==================================================

🧪 Тестирование PostgreSQL...
  ✅ Создание продукта
  ✅ Чтение продукта по external_id
  ✅ Получение списка продуктов
  ✅ Удаление продукта

🧪 Тестирование Qdrant...
  ✅ Проверка существования коллекции
  ✅ Получение информации о коллекции
  ✅ Добавление вектора (с автоматическим UUID)
  ✅ Поиск похожих векторов (score=1.0000)
  ✅ Удаление вектора

==================================================
  🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!
==================================================
```

### 🚀 Готово к использованию

Все модули работают корректно:
- ✅ PostgreSQL с SQLAlchemy 2.0 async
- ✅ Qdrant с автоматической конвертацией ID в UUID
- ✅ Все CRUD операции
- ✅ Векторный поиск
- ✅ Логирование поисковых запросов

### 📝 Примеры использования

#### PostgreSQL
```python
from app.db import get_session, create_product, get_product_by_external_id

async with get_session() as session:
    # Создание
    product = await create_product(session, {
        "external_id": "prod_001",
        "title": "Красный диван",
        "category": "мебель",
        "price": 599.99,
        "currency": "USD",
        "product_metadata": {
            "color": "red",
            "material": "fabric",
            "seats": 3
        }
    })
    
    # Чтение
    found = await get_product_by_external_id(session, "prod_001")
    print(f"Найден: {found.title}")
    print(f"Метаданные: {found.product_metadata}")
```

#### Qdrant
```python
from app.db import QdrantManager

manager = QdrantManager()

# Создание коллекции
await manager.create_collection(vector_size=512, distance="Cosine")

# Добавление векторов (ID автоматически конвертируются в UUID)
await manager.upsert_vectors(
    product_ids=["prod_001", "prod_002", "prod_003"],
    vectors=[embedding1, embedding2, embedding3],
    payloads=[
        {"title": "Красный диван", "category": "мебель"},
        {"title": "Синий стул", "category": "мебель"},
        {"title": "Деревянный стол", "category": "мебель"}
    ]
)

# Поиск похожих (возвращает оригинальные product_id)
results = await manager.search_similar(
    query_vector=query_embedding,
    top_k=10,
    score_threshold=0.7
)

for result in results:
    print(f"ID: {result['id']}")  # "prod_001"
    print(f"Score: {result['score']:.2f}")
    print(f"Title: {result['payload']['title']}")
```

### 🎯 Итоги

Все проблемы исправлены, модули полностью функциональны и готовы к интеграции в систему визуального поиска! 🚀

