# Руководство по тестированию системы

Пошаговая инструкция для проверки работоспособности всех компонентов системы визуального поиска.

## Предварительные требования

Убедитесь, что установлены:
- ✅ Docker
- ✅ Docker Compose
- ✅ Poetry
- ✅ Python 3.9+

---

## Шаг 1: Запуск Docker-контейнеров

### 1.1. Перейдите в директорию проекта

```bash
cd /home/user/Desktop/BakaiMarket/visual-search-project
```

### 1.2. Запустите Docker Compose

```bash
docker-compose up -d
```

**Ожидаемый вывод:**
```
Creating network "visual-search-project_visual_search_network" ... done
Creating visual_search_postgres ... done
Creating visual_search_redis    ... done
Creating visual_search_qdrant   ... done
```

### 1.3. Подождите несколько секунд

Сервисы должны инициализироваться:
```bash
sleep 10
```

---

## Шаг 2: Проверка запущенных контейнеров

### 2.1. Проверьте статус всех контейнеров

```bash
docker-compose ps
```

**Ожидаемый вывод (все контейнеры должны быть "Up"):**
```
         Name                       Command               State                    Ports                  
----------------------------------------------------------------------------------------------------------
visual_search_postgres   docker-entrypoint.sh postgres    Up      0.0.0.0:5432->5432/tcp
visual_search_qdrant     ./entrypoint.sh                  Up      0.0.0.0:6333->6333/tcp, 0.0.0.0:6334->6334/tcp
visual_search_redis      docker-entrypoint.sh redis ...   Up      0.0.0.0:6379->6379/tcp
```

### 2.2. Проверьте логи (если есть проблемы)

```bash
# Все логи
docker-compose logs

# Логи конкретного сервиса
docker-compose logs postgres
docker-compose logs redis
docker-compose logs qdrant
```

---

## Шаг 3: Проверка PostgreSQL

### 3.1. Подключитесь к PostgreSQL

```bash
docker exec -it visual_search_postgres psql -U postgres -d visual_search
```

## Шаг 3: Проверка PostgreSQL

### 3.1. Подключитесь к PostgreSQL
```bash
docker exec -it visual_search_postgres psql -U bakaimarket -d market
```

### 3.2. Выполните тестовые команды
```sql
-- Проверить версию PostgreSQL
SELECT version();

-- Список таблиц
\dt

-- Ожидаемый вывод:
--              List of relations
--  Schema |    Name     | Type  |    Owner    
-- --------+-------------+-------+-------------
--  public | products    | table | bakaimarket
--  public | search_logs | table | bakaimarket

-- Просмотр данных в таблице products
SELECT * FROM products;

-- Количество продуктов
SELECT COUNT(*) FROM products;

-- Структура таблицы
\d products

-- Выход
\q
```

### 3.3. Альтернативный способ проверки
```bash
# Проверка подключения
docker exec visual_search_postgres pg_isready -U bakaimarket

# Ожидаемый вывод:
# /var/run/postgresql:5432 - accepting connections

# Быстрая проверка таблиц
docker exec -it visual_search_postgres psql -U bakaimarket -d market -c "\dt"

# Быстрая проверка данных
docker exec -it visual_search_postgres psql -U bakaimarket -d market -c "SELECT COUNT(*) FROM products;"
```

### 3.4. Подключение с хоста
```bash
# Установите psql, если еще не установлен
sudo apt install postgresql-client

# Подключитесь
psql -h localhost -p 5432 -U bakaimarket -d market
# Пароль: market (из .env файла)
```

---

## Шаг 4: Проверка Qdrant

### 4.1. Откройте Qdrant UI в браузере

```
http://localhost:6333/dashboard
```

**Что вы должны увидеть:**
- Веб-интерфейс Qdrant
- Пока нет коллекций (они создадутся позже)

### 4.2. Проверьте API через curl

```bash
# Проверка здоровья
curl http://localhost:6333/

# Ожидаемый вывод:
# {"title":"qdrant - vector search engine","version":"..."}

# Список коллекций (пока пустой)
curl http://localhost:6333/collections

# Ожидаемый вывод:
# {"result":{"collections":[]},"status":"ok","time":0.000...}
```

### 4.3. Проверьте метрики

```bash
curl http://localhost:6333/metrics
```

---

## Шаг 5: Проверка Redis

### 5.1. Подключитесь к Redis CLI

```bash
docker exec -it visual_search_redis redis-cli
```

### 5.2. Выполните тестовые команды

```redis
# Проверка подключения
PING
# Ожидаемый вывод: PONG

# Установить тестовое значение
SET test_key "Hello Redis"
# Ожидаемый вывод: OK

# Получить значение
GET test_key
# Ожидаемый вывод: "Hello Redis"

# Удалить тестовый ключ
DEL test_key
# Ожидаемый вывод: (integer) 1

# Выход
exit
```

### 5.3. Альтернативная проверка

```bash
# Проверка с хоста
redis-cli -h localhost -p 6379 ping
# Ожидаемый вывод: PONG
```

---

## Шаг 6: Установка Python зависимостей

### 6.1. Проверьте, что Poetry установлен

```bash
poetry --version
```

**Если Poetry не установлен:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 6.2. Установите зависимости

```bash
poetry install
```

**Ожидаемый вывод:**
```
Installing dependencies from lock file

Package operations: XX installs, 0 updates, 0 removals

  • Installing ...
  • Installing ...
  ...
  
Installing the current project: visual-search-project (0.1.0)
```

**Это займет несколько минут** (особенно установка PyTorch).

### 6.3. Проверьте установку

```bash
# Активируйте виртуальное окружение
poetry shell

# Проверьте Python
python --version

# Проверьте установленные пакеты
poetry show
```

---

## Шаг 7: Инициализация базы данных

### 7.1. Создайте таблицы и загрузите тестовые данные

```bash
poetry run python scripts/load_sample_data.py
```

**Ожидаемый вывод:**
```
============================================================
Loading Sample Data for Visual Search Project
============================================================

Connecting to PostgreSQL...
Creating tables...
Inserting sample products...
  ✓ Inserted prod_001
  ✓ Inserted prod_002
  ✓ Inserted prod_003

Sample data loaded successfully!

Connecting to Qdrant...
Creating collection...
Qdrant collection initialized successfully!

============================================================
Setup complete!
============================================================
```

### 7.2. Проверьте созданные таблицы

```bash
docker exec -it visual_search_postgres psql -U postgres -d visual_search -c "\dt"
```

**Ожидаемый вывод:**
```
              List of relations
 Schema |     Name     | Type  |  Owner   
--------+--------------+-------+----------
 public | products     | table | postgres
 public | search_logs  | table | postgres
```

### 7.3. Проверьте данные

```bash
docker exec -it visual_search_postgres psql -U postgres -d visual_search -c "SELECT external_id, title FROM products;"
```

**Ожидаемый вывод:**
```
 external_id |         title         
-------------+-----------------------
 prod_001    | Modern Sofa
 prod_002    | Wooden Dining Table
 prod_003    | Sports Car
```

---

## Шаг 8: Запуск API сервера

### 8.1. Запустите FastAPI сервер

```bash
poetry run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Ожидаемый вывод:**
```
INFO:     Will watch for changes in these directories: ['/home/user/Desktop/BakaiMarket/visual-search-project']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXXX] using StatReload
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Оставьте этот терминал открытым!**

---

## Шаг 9: Тестирование API

Откройте **новый терминал** для тестирования.

### 9.1. Проверьте health endpoint

```bash
curl http://localhost:8000/api/v1/health
```

**Ожидаемый вывод:**
```json
{
  "status": "healthy",
  "service": "visual-search-project",
  "version": "0.1.0"
}
```

### 9.2. Проверьте детальный health check

```bash
curl http://localhost:8000/api/v1/health/detailed
```

**Ожидаемый вывод:**
```json
{
  "status": "healthy",
  "service": "visual-search-project",
  "version": "0.1.0",
  "components": {
    "postgres": "healthy",
    "qdrant": "healthy"
  }
}
```

### 9.3. Откройте интерактивную документацию

Откройте в браузере:
```
http://localhost:8000/docs
```

**Что вы должны увидеть:**
- Swagger UI с документацией API
- Список всех endpoints
- Возможность тестировать API прямо в браузере

### 9.4. Протестируйте получение продуктов

```bash
curl http://localhost:8000/api/v1/products
```

**Ожидаемый вывод:** JSON массив с продуктами

### 9.5. Протестируйте текстовый поиск

```bash
curl -X POST "http://localhost:8000/api/v1/search/text?query=sofa&limit=5"
```

**Примечание:** Первый запрос может занять время (загрузка CLIP модели).

---

## Шаг 10: Запуск Celery Worker (опционально)

### 10.1. Откройте еще один новый терминал

```bash
cd /home/user/Desktop/BakaiMarket/visual-search-project
poetry shell
```

### 10.2. Запустите Celery worker

```bash
celery -A app.workers.celery_app worker --loglevel=info
```

**Ожидаемый вывод:**
```
 -------------- celery@hostname v5.3.4 (emerald-rush)
--- ***** ----- 
-- ******* ---- Linux-6.14.0-33-generic-x86_64-with-glibc2.35 2025-11-05 15:00:00
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         visual_search_workers:0x...
- ** ---------- .> transport:   redis://localhost:6379/1
- ** ---------- .> results:     redis://localhost:6379/2
- *** --- * --- .> concurrency: 4 (prefork)
-- ******* ---- .> task events: OFF
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . app.workers.tasks.batch_index_products
  . app.workers.tasks.index_product
  . app.workers.tasks.reindex_all_products

[2025-11-05 15:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/1
[2025-11-05 15:00:00,000: INFO/MainProcess] mingle: searching for neighbors
[2025-11-05 15:00:00,000: INFO/MainProcess] mingle: all alone
[2025-11-05 15:00:00,000: INFO/MainProcess] celery@hostname ready.
```

---

## Шаг 11: Запуск тестов

### 11.1. Запустите тесты

```bash
poetry run pytest
```

**Ожидаемый вывод:**
```
============================= test session starts ==============================
platform linux -- Python 3.9.x, pytest-7.4.3, pluggy-1.3.0
rootdir: /home/user/Desktop/BakaiMarket/visual-search-project
collected X items

tests/test_api.py ...                                                    [ 50%]
tests/test_clip_model.py .....                                           [100%]

============================== X passed in X.XXs ===============================
```

### 11.2. Запустите тесты с покрытием

```bash
poetry run pytest --cov=app --cov-report=term
```

---

## Шаг 12: Проверка всех компонентов (чеклист)

Используйте этот чеклист для финальной проверки:

```bash
# Создайте скрипт проверки
cat > check_all.sh << 'EOF'
#!/bin/bash

echo "=== Проверка всех компонентов ==="
echo ""

# 1. Docker контейнеры
echo "1. Проверка Docker контейнеров..."
docker-compose ps | grep "Up" && echo "✅ Docker контейнеры запущены" || echo "❌ Проблема с Docker"
echo ""

# 2. PostgreSQL
echo "2. Проверка PostgreSQL..."
docker exec visual_search_postgres pg_isready -U postgres > /dev/null 2>&1 && echo "✅ PostgreSQL работает" || echo "❌ PostgreSQL недоступен"
echo ""

# 3. Redis
echo "3. Проверка Redis..."
docker exec visual_search_redis redis-cli ping > /dev/null 2>&1 && echo "✅ Redis работает" || echo "❌ Redis недоступен"
echo ""

# 4. Qdrant
echo "4. Проверка Qdrant..."
curl -s http://localhost:6333/ > /dev/null 2>&1 && echo "✅ Qdrant работает" || echo "❌ Qdrant недоступен"
echo ""

# 5. API (если запущен)
echo "5. Проверка API..."
curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1 && echo "✅ API работает" || echo "⚠️  API не запущен (это нормально, если вы его еще не запустили)"
echo ""

# 6. Таблицы в БД
echo "6. Проверка таблиц в БД..."
TABLES=$(docker exec visual_search_postgres psql -U postgres -d visual_search -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null | tr -d ' ')
if [ "$TABLES" -ge "2" ]; then
    echo "✅ Таблицы созданы ($TABLES таблиц)"
else
    echo "⚠️  Таблицы не созданы (запустите: poetry run python scripts/load_sample_data.py)"
fi
echo ""

# 7. Коллекция Qdrant
echo "7. Проверка коллекции Qdrant..."
curl -s http://localhost:6333/collections 2>/dev/null | grep -q "product_embeddings" && echo "✅ Коллекция Qdrant создана" || echo "⚠️  Коллекция не создана (запустите: poetry run python scripts/load_sample_data.py)"
echo ""

echo "=== Проверка завершена ==="
EOF

chmod +x check_all.sh
./check_all.sh
```

---

## Полезные команды

### Остановка всех сервисов

```bash
# Остановить Docker контейнеры
docker-compose down

# Остановить API (в терминале где он запущен)
# Нажмите Ctrl+C

# Остановить Celery worker (в терминале где он запущен)
# Нажмите Ctrl+C
```

### Перезапуск сервисов

```bash
# Перезапустить все Docker контейнеры
docker-compose restart

# Перезапустить конкретный сервис
docker-compose restart postgres
docker-compose restart redis
docker-compose restart qdrant
```

### Очистка данных

```bash
# Удалить все контейнеры и volumes
docker-compose down -v

# Очистить Python кэш
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
```

### Просмотр логов

```bash
# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f qdrant
```

---

## Решение проблем

### Проблема: Порты уже заняты

```bash
# Проверьте, какие процессы используют порты
sudo lsof -i :5432  # PostgreSQL
sudo lsof -i :6379  # Redis
sudo lsof -i :6333  # Qdrant
sudo lsof -i :8000  # API

# Измените порты в .env файле или остановите конфликтующие сервисы
```

### Проблема: Docker контейнеры не запускаются

```bash
# Проверьте логи
docker-compose logs

# Пересоздайте контейнеры
docker-compose down
docker-compose up -d --force-recreate
```

### Проблема: Poetry не находит зависимости

```bash
# Обновите Poetry
poetry self update

# Очистите кэш
poetry cache clear pypi --all

# Переустановите зависимости
rm -rf .venv
poetry install
```

### Проблема: CLIP модель не загружается

```bash
# Проверьте интернет-соединение
# Модель загружается из HuggingFace при первом запуске

# Проверьте доступное место на диске
df -h

# Проверьте логи API сервера
```

---

## Следующие шаги

После успешной проверки всех компонентов:

1. ✅ Изучите документацию API: http://localhost:8000/docs
2. ✅ Прочитайте примеры использования: `API_EXAMPLES.md`
3. ✅ Изучите архитектуру: `ARCHITECTURE.md`
4. ✅ Начните разработку своих функций

---

**Удачи в тестировании! 🚀**

