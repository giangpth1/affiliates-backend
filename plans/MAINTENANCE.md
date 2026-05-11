---
title: Maintenance & Operations
version: 1.0.0
updated: 2026-05-06
---

# Maintenance & Operations Guide

## Overview

Hướng dẫn này bao gồm backup procedures, disaster recovery, troubleshooting, và documentation update workflows.

---

## Backup & Disaster Recovery

### 1. Cosmos DB Backup

**Automatic Continuous Backup** (khuyến nghị cho production):

1. Vào Cosmos DB account → **Backup & Restore** → chọn **Continuous** mode → **Save**

**Restore**:
1. Vào Cosmos DB account → **Backup & Restore** → **Restore**
2. Chọn timestamp, nhập target database name

**Manual Export Backup** (weekly scheduled):

```python
# scripts/backup_cosmos.py
"""
Weekly backup: export all containers to JSON.
Schedule via Azure Function Timer Trigger.
"""
import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'
django.setup()

from services.cosmos_db import CosmosDBService
from azure.storage.blob import BlobServiceClient
from django.conf import settings
import json
from datetime import datetime

def backup_container(container_name: str, blob_client: BlobServiceClient):
    container = CosmosDBService.get_container(container_name)
    
    # Query all documents
    query = "SELECT * FROM c"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    
    # Upload to blob storage
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    blob_name = f"backups/{container_name}/{timestamp}.json"
    
    blob_container = blob_client.get_container_client('backups')
    blob_container.upload_blob(
        name=blob_name,
        data=json.dumps(items, indent=2, ensure_ascii=False),
        overwrite=True
    )
    
    print(f"✓ Backed up {len(items)} items from {container_name} to {blob_name}")

if __name__ == '__main__':
    blob_client = BlobServiceClient.from_connection_string(
        settings.AZURE_STORAGE_CONNECTION_STRING
    )
    
    for container in ['products', 'links']:
        backup_container(container, blob_client)
```

**Retention**: 30 days continuous backup + 12 weekly exports.

---

### 2. Azure Storage Backup

**Blob versioning + soft delete**:

1. Vào Storage account → **Data protection**
2. Bật **Blob versioning** + **Soft delete** (7 days retention)
3. Vào **Lifecycle management** → tạo rule để move old versions sang cool tier

**lifecycle-policy.json**:
```json
{
  "rules": [
    {
      "enabled": true,
      "name": "move-to-cool",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "version": {
            "tierToCool": {
              "daysAfterCreationGreaterThan": 30
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["thumbnails/"]
        }
      }
    }
  ]
}
```

---

### 3. Azure AI Search Index Backup

**Export index schema + data**:

```python
# scripts/backup_search_index.py
"""Manual backup of search index. Run monthly."""
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from django.conf import settings
import json

index_client = SearchIndexClient(
    endpoint=settings.AZURE_SEARCH_ENDPOINT,
    credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY)
)

search_client = SearchClient(
    endpoint=settings.AZURE_SEARCH_ENDPOINT,
    index_name=settings.AZURE_SEARCH_INDEX,
    credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY)
)

# Backup schema
index = index_client.get_index(settings.AZURE_SEARCH_INDEX)
with open('search_index_schema.json', 'w') as f:
    json.dump(index.serialize(), f, indent=2)

# Backup documents
results = search_client.search(search_text="*", top=10000)
docs = [dict(doc) for doc in results]

with open('search_index_data.json', 'w', encoding='utf-8') as f:
    json.dump(docs, f, indent=2, ensure_ascii=False)

print(f"✓ Backed up {len(docs)} documents from search index")
```

**Restore**: Re-create index từ schema JSON, re-index tất cả products từ Cosmos DB.

---

### 4. Configuration Backup

**Backup Azure resources config**:

1. Vào Resource Group → **Export template** → download `azure-resources-template.json`
2. Vào Web App → **Environment variables** → copy toàn bộ settings → lưu `webapp-settings.json`
3. Vào Function App → **Environment variables** → copy toàn bộ settings → lưu `functionapp-settings.json`

**Store in private Git repo** hoặc Azure Key Vault.

---

## Disaster Recovery Plan

### Scenario 1: Cosmos DB Data Corruption

**Recovery steps**:
1. Identify corruption timestamp từ Application Insights logs
2. Tạo new Cosmos DB account
3. Restore từ continuous backup đến timestamp trước khi corrupt
4. Update connection string trong Web App
5. Verify data integrity
6. Switch traffic (update DNS hoặc App Settings)

**RTO (Recovery Time Objective)**: < 2 hours  
**RPO (Recovery Point Objective)**: < 5 minutes (continuous backup)

---

### Scenario 2: Azure Region Outage

**Mitigation**: Multi-region deployment (future enhancement)

**Current failover** (manual):
1. Deploy backup Web App trong region khác (e.g., East Asia)
2. Replicate Cosmos DB sang backup region
3. Update Azure Traffic Manager để route traffic
4. Notify users về potential data lag

**Cost**: ~2x infrastructure cost cho geo-redundancy.

---

### Scenario 3: Accidental Data Deletion

**Example**: Xóa nhầm container hoặc bulk delete documents.

**Recovery**:
- Cosmos DB: Point-in-time restore (nếu < 30 days)
- Blob Storage: Soft delete recovery (nếu < 7 days)
- Worst case: Restore từ weekly backup JSON

**Prevention**:
- RBAC: Chỉ admin có quyền delete
- Soft delete flag thay vì hard delete
- Confirmation prompt trong admin tools

---

## Routine Maintenance Tasks

### Daily

- [ ] Check Application Insights error spike alerts
- [ ] Review health check endpoint status
- [ ] Monitor API response times (dashboard)
- [ ] Check scraping failure rate

**Automated via dashboard** — chỉ investigate nếu có alert.

---

### Weekly

- [ ] Review OpenAI token usage vs budget
- [ ] Check Cosmos DB RU consumption trends
- [ ] Analyze top search queries (optimize RAG)
- [ ] Review security alerts (Azure Security Center)
- [ ] Scan dependencies for vulnerabilities (`pip-audit`)

**Runbook**:
```bash
# Weekly maintenance script
cd backend
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\Activate.ps1  # Windows

# Update dependencies
pip install --upgrade pip
pip list --outdated

# Security scan
pip-audit

# Run tests
python manage.py test

# Check for Django security updates
pip install --upgrade django djangorestframework
```

---

### Monthly

- [ ] Review and update documentation (see checklist below)
- [ ] Manual backup của search index
- [ ] Review GDPR/compliance requirements
- [ ] Rotate non-critical API keys (optional)
- [ ] Database cleanup (delete old test data)
- [ ] Cost optimization review (Azure Cost Management)

---

### Quarterly

- [ ] Penetration testing
- [ ] Load testing (simulate 10x traffic)
- [ ] Disaster recovery drill (test restore procedure)
- [ ] Review and update SLO targets
- [ ] User feedback analysis (mobile app reviews)
- [ ] Tech debt prioritization

---

## Troubleshooting Guide

### Issue 1: High API Latency (P95 > 2s)

**Diagnosis**:
```kusto
// Application Insights
requests
| where timestamp > ago(1h)
| where duration > 2000
| summarize count() by operation_Name, bin(timestamp, 5m)
| render timechart
```

**Common causes**:
1. **Cosmos DB throttling (429)**:
   - Check `TotalRequests` metric in Cosmos DB
   - Solution: Increase RU/s hoặc optimize queries
2. **Azure Search slow**:
   - Check index size và query complexity
   - Solution: Reduce `top` parameter, optimize filters
3. **Cold start (Function App)**:
   - First request sau idle > 5 minutes
   - Solution: Upgrade to Premium plan (no cold start)

**Mitigation**:
```python
# Add timeout to external calls
import httpx

async with httpx.AsyncClient(timeout=5.0) as client:
    response = await client.get(url)
```

---

### Issue 2: Scraping Failures Spike

**Diagnosis**:
```kusto
traces
| where message contains "scraping failed"
| summarize count() by tostring(customDimensions.error_type)
```

**Common causes**:
1. **Shopee changed HTML structure**:
   - Solution: Update selectors in `services/scraper.py`
2. **Shopee rate limiting**:
   - Solution: Add exponential backoff, rotate User-Agent
3. **Network timeout**:
   - Solution: Increase timeout, retry failed jobs

**Fix example**:
```python
# services/scraper.py
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def fetch_product_page(url: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; ShopeeAffBot/1.0)'
        })
        response.raise_for_status()
        return response.text
```

---

### Issue 3: Mobile App Cannot Connect

**Checklist**:
1. Health check working? `curl https://app-shopee-aff-prod.azurewebsites.net/api/health/`
2. CORS configured? Check `CORS_ALLOWED_ORIGINS`
3. API key correct? Check mobile app config
4. Certificate valid? Check SSL cert expiry

**Debug**:
```bash
# Test API từ mobile device network
curl -H "X-API-Key: your-key" https://app-shopee-aff-prod.azurewebsites.net/api/products/

# Check Azure Web App logs qua Portal
# Vào Web App → Monitoring → Log stream
```

---

### Issue 4: Search Results Poor Quality

**Diagnosis**:
- User reports không tìm thấy sản phẩm dù đã add
- Search query "tai nghe" không match "Tai Nghe Sony"

**Solutions**:
1. **Verify indexing**:
   ```python
   # Check document count
   from services.azure_search import get_search_client
   client = get_search_client()
   print(f"Total docs: {client.get_document_count()}")
   ```

2. **Re-index all products**:
   ```python
   # scripts/reindex_all.py
   from services.cosmos_db import CosmosDBService
   from services.azure_search import AzureSearchService
   
   products = CosmosDBService.query('products', 'SELECT * FROM c WHERE c.status = "active"')
   AzureSearchService.index_products_batch(products)
   print(f"✓ Re-indexed {len(products)} products")
   ```

3. **Tune search parameters**:
   - Increase `k_nearest_neighbors` for vector search
   - Adjust BM25 weights
   - Use Vietnamese analyzer (`vi.microsoft`)

---

## Database Cleanup

### Remove Old Test Data

```python
# scripts/cleanup_test_data.py
"""
Remove links older than 90 days with status 'failed'.
Schedule monthly via cron hoặc Azure Function.
"""
from services.cosmos_db import CosmosDBService
from datetime import datetime, timedelta, timezone

cutoff_date = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()

query = """
SELECT * FROM c 
WHERE c.status = 'failed' 
AND c.created_at < @cutoff_date
"""

old_links = CosmosDBService.query('links', query, [
    {"name": "@cutoff_date", "value": cutoff_date}
])

for link in old_links:
    CosmosDBService.delete('links', link['id'], link['user_id'])
    print(f"Deleted old failed link: {link['id']}")

print(f"✓ Cleaned up {len(old_links)} old failed links")
```

---

## Documentation Update Workflow

**Khi nào phải update docs**:

### 1. Code Changes
- ✅ **API endpoint thay đổi** → Update [API_SPEC.md](API_SPEC.md)
- ✅ **Database schema thay đổi** → Update [ARCHITECTURE.md](ARCHITECTURE.md)
- ✅ **Thêm dependency mới** → Update relevant PLAN_PHASE_*.md

### 2. Infrastructure Changes
- ✅ **Azure resource mới** → Update [PLAN_PHASE_1_SETUP.md](PLAN_PHASE_1_SETUP.md)
- ✅ **Deployment process thay đổi** → Update [PLAN_PHASE_5_DEPLOY.md](PLAN_PHASE_5_DEPLOY.md)

### 3. Security/Operational Changes
- ✅ **Authentication method thay đổi** → Update [SECURITY.md](SECURITY.md)
- ✅ **Monitoring/alerting thay đổi** → Update [MONITORING.md](MONITORING.md)
- ✅ **Backup procedure thay đổi** → Update [MAINTENANCE.md](MAINTENANCE.md)

---

### Documentation Update Checklist

**Template** (copy vào PR description):

```markdown
## Documentation Updates

- [ ] Updated version number và date trong frontmatter
- [ ] Verified code snippets are correct (copy-paste testable)
- [ ] Updated architecture diagram nếu cần (dùng Mermaid hoặc Draw.io)
- [ ] Cross-referenced related docs (internal links)
- [ ] Reviewed bởi ít nhất 1 team member
- [ ] Tested Portal operations (dry-run nếu có thể)
- [ ] Updated CHANGELOG.md với summary

**Files changed:**
- `docs/API_SPEC.md` - Added new `/products/batch/` endpoint
- `docs/ARCHITECTURE.md` - Updated Cosmos DB schema for categories

**Impact:**
- Breaking changes: No
- New features: Yes (batch product upload)
```

---

### Version Control Best Practices

**File naming**:
- Current docs: `API_SPEC.md` (always latest)
- Archived: `archive/API_SPEC_v1.0.0.md` (major version changes)

**Commit messages**:
```
docs: update API_SPEC with batch endpoint

- Added POST /api/products/batch/ endpoint spec
- Updated response format with job_id for async tracking
- Closes #42
```

**Branch strategy**:
- Docs-only changes: Direct commit to `main` (sau review)
- Docs + code changes: Feature branch → PR

---

## Scaling Considerations

### When to Scale Up

**Cosmos DB**:
- Metric: RU/s consumption > 80%
- Action: Increase provisioned throughput hoặc switch to autoscale
```
Vào Cosmos DB → Data Explorer → Scale → chọn Autoscale (max 4000 RU/s)
```

**Azure Web App**:
- Metric: CPU > 70% sustained hoặc memory > 85%
- Action: Scale up (vertical) hoặc scale out (horizontal)
```
Vào App Service Plan → Scale up (App Service plan) → chọn P1v2 tier
Vào App Service Plan → Scale out (App Service plan) → set instance count = 3
```

**Azure AI Search**:
- Metric: Query latency > 500ms P95
- Action: Upgrade từ Free → Basic → Standard
- Sharding: Partition index nếu > 1M documents

---

## Support & Escalation

### Contact Points

| Issue Type | Contact | SLA |
|---|---|---|
| Production outage | On-call engineer (PagerDuty) | 15 min response |
| Performance degradation | DevOps team (Slack #alerts) | 1 hour |
| Security incident | Security team + CTO | Immediate |
| Data corruption | Database admin | 30 min |
| Billing spike | FinOps team | 1 business day |

### Azure Support

- **Plan**: Developer ($29/mo) hoặc Standard ($100/mo)
- **Ticket**: Azure Portal → Support → New request
- **Critical issues**: 24/7 phone support (Standard plan+)

### Emergency Contacts

```
# Save in team wiki
On-call rotation: https://pagerduty.com/schedules/shopee-aff
Azure subscription owner: owner@company.com
Database admin: dba@company.com
Security officer: security@company.com
```
