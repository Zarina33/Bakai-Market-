# 🚀 Быстрый старт: Мониторинг

## Запуск системы с мониторингом

### 1. Запустить API

```bash
cd /home/user/Desktop/BakaiMarket/visual-search-project
poetry run uvicorn app.api.main:app --reload
```

### 2. Проверить мониторинг

В другом терминале:

```bash
# Автоматический тест всех компонентов
poetry run python scripts/test_monitoring.py
```

### 3. Проверить метрики вручную

```bash
# Prometheus метрики
curl http://localhost:8000/api/v1/metrics

# JSON сводка
curl http://localhost:8000/api/v1/metrics/summary

# Health check
curl http://localhost:8000/api/v1/health/detailed
```

## 📊 Основные endpoints

| Endpoint | Описание |
|----------|----------|
| `GET /api/v1/metrics` | Prometheus метрики (text format) |
| `GET /api/v1/metrics/summary` | JSON сводка метрик |
| `GET /api/v1/health` | Простой health check |
| `GET /api/v1/health/detailed` | Детальный health check с метриками |

## 📝 Просмотр логов

```bash
# Основные логи приложения
tail -f logs/app_$(date +%Y-%m-%d).log

# Только ошибки
tail -f logs/errors_$(date +%Y-%m-%d).log

# HTTP access логи
tail -f logs/access_$(date +%Y-%m-%d).log
```

## 🧪 Запуск тестов

```bash
# Только тесты мониторинга
poetry run pytest tests/test_monitoring.py -v

# Все тесты
poetry run pytest -v
```

## 📈 Пример использования метрик

### Выполнить поиск

```bash
# Текстовый поиск
curl -X POST http://localhost:8000/api/v1/search/by-text \
  -H "Content-Type: application/json" \
  -d '{"query": "красный диван", "limit": 5}'
```

### Проверить метрики

```bash
# Посмотреть обновлённые метрики
curl http://localhost:8000/api/v1/metrics | grep visual_search_total_searches

# JSON сводка
curl http://localhost:8000/api/v1/metrics/summary | jq
```

## 🔧 Конфигурация

### Уровень логирования

```bash
# Development (DEBUG логи)
export DEBUG=true
poetry run uvicorn app.api.main:app --reload

# Production (INFO логи, JSON формат)
export DEBUG=false
poetry run uvicorn app.api.main:app
```

## 📊 Доступные метрики

### Counters
- `visual_search_total_searches_total` - количество поисков
- `visual_search_errors_total` - количество ошибок
- `visual_search_products_added_total` - добавленные продукты

### Histograms
- `visual_search_duration_seconds` - время поиска
- `clip_inference_duration_seconds` - время CLIP
- `qdrant_search_duration_seconds` - время Qdrant

### Gauges
- `visual_search_active_products` - активные продукты
- `visual_search_qdrant_vectors` - векторы в Qdrant
- `visual_search_api_health` - здоровье API (1=ok, 0=fail)
- `visual_search_clip_model_loaded` - CLIP модель (1=loaded, 0=not loaded)

## 🎯 Что мониторить

✅ **Производительность:**
- Время поиска (должно быть < 1s для P95)
- Время CLIP inference (должно быть < 0.5s)
- Время Qdrant поиска (должно быть < 0.1s)

✅ **Надёжность:**
- Процент ошибок (должен быть < 1%)
- API health (должен быть = 1)
- CLIP model loaded (должен быть = 1)

✅ **Ресурсы:**
- Количество продуктов
- Количество векторов
- Размер логов

## 🚨 Алерты (рекомендуется)

Настроить алерты для:
- API down (api_health == 0)
- High error rate (errors > 5%)
- Slow searches (P95 > 2s)
- CLIP model not loaded

## 📚 Документация

- **MONITORING.md** - полная документация
- **MONITORING_SUMMARY.md** - краткая сводка
- **scripts/test_monitoring.py** - интерактивный тест

## 💡 Полезные команды

```bash
# Запустить API
poetry run uvicorn app.api.main:app --reload

# Тест мониторинга
poetry run python scripts/test_monitoring.py

# Загрузить demo продукты
poetry run python scripts/load_demo_products.py

# Тест поиска
poetry run python scripts/test_search_api.py

# Все тесты
poetry run pytest -v

# Только мониторинг
poetry run pytest tests/test_monitoring.py -v
```

## ✨ Готово!

Система мониторинга полностью настроена и готова к использованию! 🎉

Для подробной информации см. **MONITORING.md**

