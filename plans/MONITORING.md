---
title: Monitoring & Logging Strategy
version: 1.0.0
updated: 2026-05-06
---

# Monitoring & Logging Strategy

## Overview

Toàn bộ hệ thống monitoring dựa trên Azure Application Insights, Azure Monitor, và structured logging để đảm bảo health visibility, performance tracking, và debugging hiệu quả.

---

## Azure Application Insights Setup

### Step 1 — Tạo Application Insights Resource (Portal)

1. Vào **Application Insights** → **+ Create**
2. Resource Group: `rg-shopee-aff-dev`, Name: `ai-shopee-aff-dev`
3. Application type: **Web**
4. **Review + create** → **Create**

**Lấy Connection String**:
1. Vào Application Insights resource → **Overview**
2. Copy **Connection String** → dùng làm `APPINSIGHTS_INSTRUMENTATION_KEY`

### Step 2 — Integrate vào Django

**requirements.txt**:
```
opencensus-ext-azure==1.1.13
opencensus-ext-django==0.8.0
opencensus-ext-logging==0.1.1
```

**config/settings/base.py**:
```python
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.django.middleware import OpencensusMiddleware

APPINSIGHTS_INSTRUMENTATION_KEY = env('APPINSIGHTS_INSTRUMENTATION_KEY')

# Middleware
MIDDLEWARE = [
    'opencensus.ext.django.middleware.OpencensusMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # ... rest
]

# OpenCensus config
OPENCENSUS = {
    'TRACE': {
        'SAMPLER': 'opencensus.trace.samplers.ProbabilitySampler(rate=1.0)',
        'EXPORTER': f'''opencensus.ext.azure.trace_exporter.AzureExporter(
            connection_string="InstrumentationKey={APPINSIGHTS_INSTRUMENTATION_KEY}"
        )''',
    }
}

# Logging config
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'azure': {
            'class': 'opencensus.ext.azure.log_exporter.AzureLogHandler',
            'connection_string': f'InstrumentationKey={APPINSIGHTS_INSTRUMENTATION_KEY}',
        },
    },
    'root': {
        'handlers': ['console', 'azure'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'azure'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'azure'],
            'level': 'INFO',
            'propagate': False,
        },
        'services': {
            'handlers': ['console', 'azure'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Step 3 — Structured Logging Best Practices

**apps/links/services.py** (example):
```python
import logging
logger = logging.getLogger(__name__)

class LinkService:
    @staticmethod
    def create(url: str, user_id: str) -> dict:
        logger.info(
            "Creating new link",
            extra={
                'custom_dimensions': {
                    'user_id': user_id,
                    'url_length': len(url),
                    'operation': 'link_create'
                }
            }
        )
        try:
            # ... logic
            logger.info(
                "Link created successfully",
                extra={'custom_dimensions': {'link_id': link['id']}}
            )
            return link
        except Exception as e:
            logger.error(
                "Link creation failed",
                extra={
                    'custom_dimensions': {
                        'user_id': user_id,
                        'error_type': type(e).__name__,
                        'operation': 'link_create'
                    }
                },
                exc_info=True
            )
            raise
```

---

## Key Metrics to Track

### 1. Application Performance

**Kusto Query (Application Insights)**:
```kusto
// API response times (P50, P95, P99)
requests
| where timestamp > ago(1h)
| summarize 
    p50=percentile(duration, 50),
    p95=percentile(duration, 95),
    p99=percentile(duration, 99)
    by operation_Name
| order by p99 desc

// Error rate
requests
| where timestamp > ago(1h)
| summarize 
    total=count(),
    errors=countif(success == false)
| extend error_rate = errors * 100.0 / total

// Slow requests (>3s)
requests
| where timestamp > ago(1h)
| where duration > 3000
| project timestamp, operation_Name, duration, url
| order by duration desc
```

### 2. Scraping Success Rate

**Custom Metric Tracking**:
```python
# services/scraper.py
from opencensus.stats import aggregation, measure, view
from opencensus.stats import stats as stats_module
from opencensus.tags import tag_map

# Define metric
scrape_duration = measure.MeasureFloat("scrape_duration", "Scraping duration", "ms")
scrape_success = measure.MeasureInt("scrape_success", "Scraping success", "1")

def track_scraping_result(success: bool, duration_ms: float):
    mmap = stats_module.stats.stats_recorder.new_measurement_map()
    tmap = tag_map.TagMap()
    
    tmap.insert("success", "true" if success else "false")
    mmap.measure_int_put(scrape_success, 1 if success else 0)
    mmap.measure_float_put(scrape_duration, duration_ms)
    mmap.record(tmap)
```

**Query**:
```kusto
customMetrics
| where name == "scrape_success"
| where timestamp > ago(24h)
| summarize 
    total=count(),
    success=countif(value == 1),
    failed=countif(value == 0)
| extend success_rate = success * 100.0 / total
```

### 3. Cosmos DB Performance

**Built-in metrics** (Azure Portal):
- Request Units (RU/s) consumption
- Throttled requests (429 errors)
- Server-side latency
- Document count growth

**Alert when**:
- RU/s > 80% provisioned capacity
- 429 error rate > 1%
- P95 latency > 500ms

### 4. Azure AI Search Performance

**Metrics to track**:
- Search queries per second
- Average search latency
- Index size and document count

```kusto
dependencies
| where type == "Azure Search"
| where timestamp > ago(1h)
| summarize 
    qps=count() / 3600.0,
    avg_duration=avg(duration),
    p95_duration=percentile(duration, 95)
```

### 5. Storage Usage
---

## Alerts Configuration

### Critical Alerts (PagerDuty/Email)

Tạo alerts qua Portal:
1. Vào **Azure Monitor** → **Alerts** → **Create** → **Alert rule**
2. Chọn scope (Web App, Cosmos DB, etc.)
3. Chọn condition:
   - **API Down**: Requests failed > 10 trong 5 phút → Severity 1
   - **High Latency**: Avg response time > 3000ms trong 5 phút → Severity 2
   - **Cosmos DB Throttling**: TotalRequests với StatusCode=429 > 5 trong 5 phút → Severity 2
4. Chọn action group (email, Slack, PagerDuty)
5. **Create**

### Warning Alerts (Slack/Email)

- Search success rate < 95%
- Scraping failure rate > 10%
- Storage cost spike

---

## Dashboard Configuration

**Azure Dashboard** — main KPIs:

1. **API Health Panel**:
   - Request rate (req/min)
   - Error rate (%)
   - P95 latency
   - Availability (uptime %)

2. **Scraping Pipeline Panel**:
   - Links submitted (today)
   - Scraping success rate
   - Average scraping time
   - Failed links (last 24h)

3. **Search Panel**:
   - Search queries (today)
   - Average search latency
   - Top searched keywords

4. **Cost Panel**:
   - Cosmos DB RU consumption
   - Storage usage (GB)
   - Estimated monthly cost

---

## Log Retention Policy

| Log Type | Retention | Storage |
|---|---|---|
| Application logs | 90 days | Application Insights |
| Access logs | 30 days | Azure Storage (archive) |
| Error logs | 180 days | Application Insights |
| Audit logs | 1 year | Azure Storage (cool tier) |

---

## Performance Targets (SLO)

| Metric | Target | Measurement |
|---|---|---|
| API Availability | 99.5% | Monthly uptime |
| API P95 Latency | < 500ms | Excluding scraping |
| Scraping Success Rate | > 95% | Valid Shopee URLs |
| Search Latency | < 300ms | P95 hybrid search |
| Error Rate | < 1% | 4xx + 5xx / total |

---

## Troubleshooting Queries

### 1. Find slow API endpoints
```kusto
requests
| where timestamp > ago(1h)
| where duration > 1000
| summarize count(), avg(duration), max(duration) by operation_Name
| order by avg_duration desc
```

### 2. Trace failed scraping jobs
```kusto
traces
| where message contains "scraping failed"
| extend link_id = tostring(customDimensions.link_id)
| extend error = tostring(customDimensions.error_type)
| project timestamp, link_id, error, message
| order by timestamp desc
```

### 3. Find dependencies causing timeouts
```kusto
dependencies
| where timestamp > ago(1h)
| where duration > 5000
| summarize count() by type, target, name
| order by count_ desc
```

### 4. User journey tracking
```kusto
// Theo dõi 1 link từ lúc tạo đến done
let link_id = "your-link-id";
union traces, requests, dependencies
| where customDimensions.link_id == link_id or operation_Id contains link_id
| project timestamp, itemType, operation_Name, message, duration
| order by timestamp asc
```

---

## Flutter App Analytics

**Firebase Analytics** (optional, cho mobile):
```dart
// lib/core/analytics.dart
import 'package:firebase_analytics/firebase_analytics.dart';

class Analytics {
  static final _analytics = FirebaseAnalytics.instance;

  static void logLinkSubmitted() {
    _analytics.logEvent(name: 'link_submitted');
  }

  static void logSearchPerformed(String query) {
    _analytics.logEvent(
      name: 'search_performed',
      parameters: {'query_length': query.length},
    );
  }

  static void logError(String errorType) {
    _analytics.logEvent(
      name: 'error_occurred',
      parameters: {'error_type': errorType},
    );
  }
}
```

---

## Health Check Endpoint

**apps/core/views.py**:
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def health_check(request):
    """
    Comprehensive health check.
    Returns 200 if all critical services are reachable.
    """
    status = {'status': 'healthy', 'checks': {}}
    http_status = 200

    # Check Cosmos DB
    try:
        from services.cosmos_db import CosmosDBService
        CosmosDBService.get_database().read()
        status['checks']['cosmos_db'] = 'ok'
    except Exception as e:
        status['checks']['cosmos_db'] = f'error: {str(e)}'
        status['status'] = 'degraded'
        http_status = 503

    # Check Azure Search
    try:
        from services.azure_search import get_search_client
        client = get_search_client()
        client.get_document_count()
        status['checks']['azure_search'] = 'ok'
    except Exception as e:
        status['checks']['azure_search'] = f'error: {str(e)}'
        status['status'] = 'degraded'

    # Check Azure Storage
    try:
        from azure.storage.blob import BlobServiceClient
        from django.conf import settings
        client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        list(client.list_containers(max_results=1))
        status['checks']['azure_storage'] = 'ok'
    except Exception as e:
        status['checks']['azure_storage'] = f'error: {str(e)}'
        status['status'] = 'degraded'

    logger.info(f"Health check: {status['status']}", extra={
        'custom_dimensions': status['checks']
    })

    return Response(status, status=http_status)
```

**Uptime monitoring** — ping endpoint mỗi 5 phút:
1. Vào Application Insights → **Availability** → **Add Standard test**
2. URL: `https://app-shopee-aff-dev.azurewebsites.net/api/health/`
3. Frequency: 5 minutes, Timeout: 30 seconds
4. **Create**
