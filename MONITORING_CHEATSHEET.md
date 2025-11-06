# 📋 Шпаргалка по мониторингу

## Быстрые команды

### Запуск
```bash
# Запустить API с мониторингом
poetry run uvicorn app.api.main:app --reload

# Тест мониторинга
poetry run python scripts/test_monitoring.py
```

### Проверка метрик
```bash
# Prometheus метрики
curl http://localhost:8000/api/v1/metrics

# JSON сводка
curl http://localhost:8000/api/v1/metrics/summary | jq

# Health check
curl http://localhost:8000/api/v1/health/detailed | jq
```

### Логи
```bash
# Основные логи (real-time)
tail -f logs/app_$(date +%Y-%m-%d).log

# Только ошибки
tail -f logs/errors_$(date +%Y-%m-%d).log

# HTTP requests
tail -f logs/access_$(date +%Y-%m-%d).log

# Поиск в логах
grep "ERROR" logs/app_*.log
grep "search" logs/access_*.log
```

### Тесты
```bash
# Только мониторинг
pytest tests/test_monitoring.py -v

# Все тесты
pytest -v

# С покрытием
pytest --cov=app tests/
```

## Основные метрики

| Метрика | Тип | Описание |
|---------|-----|----------|
| `visual_search_total_searches_total` | Counter | Количество поисков |
| `visual_search_duration_seconds` | Histogram | Время поиска |
| `clip_inference_duration_seconds` | Histogram | Время CLIP |
| `visual_search_api_health` | Gauge | Здоровье API (1=ok) |
| `visual_search_active_products` | Gauge | Количество продуктов |

## Endpoints

| URL | Метод | Описание |
|-----|-------|----------|
| `/api/v1/metrics` | GET | Prometheus метрики |
| `/api/v1/metrics/summary` | GET | JSON сводка |
| `/api/v1/health` | GET | Простой health |
| `/api/v1/health/detailed` | GET | Детальный health |

## Prometheus запросы

```promql
# Количество запросов/сек
rate(visual_search_total_searches_total[5m])

# Средняя длительность
rate(visual_search_duration_seconds_sum[5m]) / rate(visual_search_duration_seconds_count[5m])

# P95 латентность
histogram_quantile(0.95, rate(visual_search_duration_seconds_bucket[5m]))

# Процент ошибок
rate(visual_search_errors_total[5m]) / rate(visual_search_total_searches_total[5m]) * 100
```

## Алерты

```yaml
# API Down
expr: visual_search_api_health == 0
for: 1m

# High Error Rate
expr: rate(visual_search_errors_total[5m]) / rate(visual_search_total_searches_total[5m]) > 0.05
for: 5m

# Slow Searches
expr: histogram_quantile(0.95, rate(visual_search_duration_seconds_bucket[5m])) > 2
for: 5m
```

## Troubleshooting

### API не отвечает
```bash
# Проверить процесс
ps aux | grep uvicorn

# Проверить порт
netstat -tulpn | grep 8000

# Проверить логи
tail -50 logs/errors_*.log
```

### Метрики не обновляются
```bash
# Вызвать health check (обновит gauge метрики)
curl http://localhost:8000/api/v1/health/detailed

# Проверить метрики
curl http://localhost:8000/api/v1/metrics | grep visual_search
```

### Логи не пишутся
```bash
# Проверить директорию
ls -la logs/

# Создать если нет
mkdir -p logs

# Проверить права
chmod 755 logs
```

## Полезные ссылки

- **Полная документация**: `MONITORING.md`
- **Сводка**: `MONITORING_SUMMARY.md`
- **Быстрый старт**: `QUICKSTART_MONITORING.md`
- **Тесты**: `tests/test_monitoring.py`
- **Скрипт**: `scripts/test_monitoring.py`

