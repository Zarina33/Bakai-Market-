# Мониторинг и метрики

Система визуального поиска включает полноценный мониторинг с Prometheus метриками и структурированным логированием.

## 📊 Prometheus Метрики

### Endpoints

#### GET /api/v1/metrics
Prometheus metrics endpoint для scraping.

**Формат**: Prometheus text format  
**Content-Type**: `text/plain; version=0.0.4`

**Пример использования**:
```bash
curl http://localhost:8000/api/v1/metrics
```

#### GET /api/v1/metrics/summary
JSON сводка основных метрик.

**Пример ответа**:
```json
{
  "status": "ok",
  "metrics": {
    "api_health": 1,
    "clip_model_loaded": 1,
    "active_products": 15,
    "qdrant_vectors": 15
  }
}
```

### Доступные метрики

#### Counters (счётчики)

**`visual_search_total_searches_total{search_type}`**
- Общее количество поисковых запросов
- Labels: `search_type` (by-image, by-text, similar)

**`visual_search_errors_total{error_type}`**
- Общее количество ошибок поиска
- Labels: `error_type` (by-image, by-text, similar)

**`visual_search_products_added_total`**
- Общее количество добавленных продуктов

#### Histograms (гистограммы)

**`visual_search_duration_seconds{search_type}`**
- Длительность поисковых запросов в секундах
- Labels: `search_type` (by-image, by-text, similar)
- Buckets: [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]

**`clip_inference_duration_seconds`**
- Длительность CLIP inference в секундах
- Buckets: [0.01, 0.05, 0.1, 0.5, 1.0]

**`qdrant_search_duration_seconds`**
- Длительность поиска в Qdrant в секундах
- Buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]

#### Gauges (текущие значения)

**`visual_search_active_products`**
- Количество активных продуктов в базе данных

**`visual_search_qdrant_vectors`**
- Количество векторов в Qdrant коллекции

**`visual_search_api_health`**
- Статус здоровья API (1=healthy, 0=unhealthy)

**`visual_search_clip_model_loaded`**
- Статус загрузки CLIP модели (1=loaded, 0=not loaded)

## 📝 Логирование

### Структура логов

Система использует **loguru** для структурированного логирования.

#### Уровни логирования

- **DEBUG**: Детальная информация для отладки (только в dev режиме)
- **INFO**: Общая информация о работе системы
- **WARNING**: Предупреждения о потенциальных проблемах
- **ERROR**: Ошибки, требующие внимания

### Файлы логов

Логи сохраняются в директории `logs/`:

#### `logs/app_YYYY-MM-DD.log`
- Основные логи приложения
- Ротация: ежедневно в 00:00
- Хранение: 30 дней
- Сжатие: zip

#### `logs/errors_YYYY-MM-DD.log`
- Только ошибки (ERROR и выше)
- Ротация: ежедневно в 00:00
- Хранение: 90 дней
- Сжатие: zip
- Включает полный traceback

#### `logs/access_YYYY-MM-DD.log`
- HTTP access логи
- Ротация: ежедневно в 00:00
- Хранение: 14 дней
- Сжатие: zip

### Формат логов

#### Development (DEBUG=True)
Красивые цветные логи в консоли:
```
2025-11-06 16:10:11 | INFO     | app.api.main:startup_event - Starting Visual Search API...
```

#### Production (DEBUG=False)
JSON логи для парсинга:
```json
{
  "text": "Starting Visual Search API...",
  "record": {
    "time": {"timestamp": 1762423811.957306},
    "level": {"name": "INFO"},
    "message": "Starting Visual Search API...",
    "module": "main",
    "function": "startup_event",
    "extra": {}
  }
}
```

### HTTP Request Logging

Все HTTP запросы автоматически логируются через `LoggingMiddleware`:

**Входящий запрос**:
```
→ GET /api/v1/search/by-text
```

**Исходящий ответ**:
```
← GET /api/v1/search/by-text - 200 - 0.523s
```

**Дополнительные поля**:
- `request_id`: Уникальный ID запроса
- `method`: HTTP метод
- `path`: URL путь
- `status_code`: Код ответа
- `duration`: Длительность в секундах
- `client_host`: IP клиента
- `user_agent`: User-Agent клиента

**HTTP заголовок**: `X-Process-Time` содержит время обработки запроса в секундах.

## 🔧 Конфигурация

### Настройка логирования

Логирование настраивается автоматически при старте приложения через `setup_logging()`.

Для изменения уровня логирования установите переменную окружения:
```bash
export DEBUG=true  # Для DEBUG логов
export DEBUG=false # Для INFO логов (production)
```

### Интеграция с Prometheus

#### Локальное тестирование

```bash
# Запустить API
poetry run uvicorn app.api.main:app --reload

# Проверить метрики
curl http://localhost:8000/api/v1/metrics
```

#### Конфигурация Prometheus

Добавьте в `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'visual-search-api'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/metrics'
```

#### Grafana Dashboard

Примеры запросов для Grafana:

**Количество запросов по типу**:
```promql
rate(visual_search_total_searches_total[5m])
```

**Средняя длительность поиска**:
```promql
rate(visual_search_duration_seconds_sum[5m]) / rate(visual_search_duration_seconds_count[5m])
```

**P95 длительность CLIP inference**:
```promql
histogram_quantile(0.95, rate(clip_inference_duration_seconds_bucket[5m]))
```

**Процент ошибок**:
```promql
rate(visual_search_errors_total[5m]) / rate(visual_search_total_searches_total[5m]) * 100
```

**Статус здоровья API**:
```promql
visual_search_api_health
```

## 🚨 Алертинг

### Рекомендуемые алерты

#### API Down
```yaml
- alert: VisualSearchAPIDown
  expr: visual_search_api_health == 0
  for: 1m
  annotations:
    summary: "Visual Search API is down"
```

#### High Error Rate
```yaml
- alert: HighErrorRate
  expr: rate(visual_search_errors_total[5m]) / rate(visual_search_total_searches_total[5m]) > 0.05
  for: 5m
  annotations:
    summary: "High error rate (>5%) in Visual Search API"
```

#### Slow Searches
```yaml
- alert: SlowSearches
  expr: histogram_quantile(0.95, rate(visual_search_duration_seconds_bucket[5m])) > 2
  for: 5m
  annotations:
    summary: "P95 search duration is above 2 seconds"
```

#### CLIP Model Not Loaded
```yaml
- alert: CLIPModelNotLoaded
  expr: visual_search_clip_model_loaded == 0
  for: 1m
  annotations:
    summary: "CLIP model is not loaded"
```

## 📈 Мониторинг в коде

### Запись метрик

```python
from app.utils.metrics import (
    record_search,
    record_clip_inference,
    record_qdrant_search,
    record_product_added,
    update_active_products,
    update_qdrant_vectors,
)

# Записать поисковый запрос
record_search("by-image", duration=0.5, success=True)

# Записать CLIP inference
record_clip_inference(duration=0.1)

# Записать Qdrant поиск
record_qdrant_search(duration=0.01)

# Записать добавление продукта
record_product_added()

# Обновить gauge метрики
update_active_products(100)
update_qdrant_vectors(200)
```

### Логирование

```python
from loguru import logger

# Обычное логирование
logger.info("Processing image search")
logger.warning("Slow query detected")
logger.error("Failed to connect to database")

# С дополнительными полями
logger.bind(user_id="123").info("User search completed")

# С исключением
try:
    # some code
except Exception as e:
    logger.exception("Error processing request")
```

## 🧪 Тестирование

Запустить тесты мониторинга:

```bash
poetry run pytest tests/test_monitoring.py -v
```

Тесты проверяют:
- ✅ Metrics endpoint
- ✅ Metrics summary endpoint  
- ✅ Health check обновляет метрики
- ✅ Запись метрик поиска
- ✅ Запись метрик CLIP inference
- ✅ Запись метрик Qdrant
- ✅ Запись метрик продуктов
- ✅ Обновление gauge метрик
- ✅ Logging middleware
- ✅ Формат Prometheus метрик

## 📊 Health Checks

### GET /api/v1/health
Простой health check.

**Ответ**:
```json
{
  "status": "healthy",
  "service": "Visual Search API",
  "version": "0.1.0"
}
```

### GET /api/v1/health/detailed
Детальный health check с проверкой всех компонентов.

**Ответ**:
```json
{
  "status": "healthy",
  "service": "Visual Search API",
  "version": "0.1.0",
  "components": {
    "postgresql": {
      "status": "healthy",
      "products_count": 15
    },
    "qdrant": {
      "status": "healthy",
      "vectors_count": 15,
      "collection": "products"
    }
  }
}
```

При вызове `/health/detailed` автоматически обновляются метрики:
- `visual_search_active_products`
- `visual_search_qdrant_vectors`
- `visual_search_api_health`

## 🎯 Best Practices

1. **Регулярно проверяйте метрики** через `/api/v1/metrics/summary`
2. **Настройте алерты** для критичных метрик
3. **Мониторьте логи ошибок** в `logs/errors_*.log`
4. **Используйте structured logging** с дополнительными полями
5. **Проверяйте health endpoints** перед деплоем
6. **Анализируйте P95/P99** длительности запросов
7. **Отслеживайте процент ошибок** и устанавливайте SLO

## 🔍 Troubleshooting

### Метрики не обновляются
- Проверьте, что API запущен
- Вызовите `/api/v1/health/detailed` для обновления gauge метрик
- Проверьте логи на ошибки

### Логи не пишутся в файлы
- Проверьте права доступа к директории `logs/`
- Убедитесь, что `setup_logging()` вызывается при старте

### Prometheus не может scrape метрики
- Проверьте доступность `/api/v1/metrics`
- Убедитесь, что firewall не блокирует порт
- Проверьте конфигурацию Prometheus

---

**Документация обновлена**: 2025-11-06  
**Версия**: 1.0

