---
title: Azure Cost Estimation & Optimization
version: 1.0.0
updated: 2026-05-06
---

# Azure Cost Estimation & Optimization

## Overview

Tài liệu này ước tính chi phí vận hành hệ thống trên Azure, breakdown theo service, và strategies để optimize costs.

**Disclaimer**: Giá có thể thay đổi. Check [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/) cho giá hiện tại.

---

## Monthly Cost Breakdown (Development Environment)

| Service | SKU/Tier | Quantity | Unit Price | Monthly Cost |
|---|---|---|---|---|
| **App Service Plan** | B2 (2 cores, 3.5GB RAM) | 1 instance | ~$70/mo | **$70** |
| **Azure Cosmos DB** | Serverless (pay-per-request) | 10M RU/mo | $0.25/1M RU | **$2.50** |
| **Azure Storage** | Standard LRS | 10 GB + 100K ops | $0.02/GB + ops | **$1** |
| **Azure AI Search** | Free tier | 1 index (50MB, 10K docs) | Free | **$0** |
| **Azure Function App** | Consumption plan | 100K executions | First 1M free | **$0** |
| **Application Insights** | Basic | 5 GB logs/mo | First 5GB free | **$0** |
| **Bandwidth** | Outbound data transfer | 10 GB/mo | First 100GB free | **$0** |

**Total Development Cost**: ~**$80/month**

---

## Monthly Cost Breakdown (Production Environment)

**Assumptions**:
- 10,000 active users
- 50,000 API requests/day
- 1,000 new links/day (30,000/mo)
- 200,000 search queries/month
- 100 GB storage (thumbnails)

| Service | SKU/Tier | Quantity | Unit Price | Monthly Cost |
|---|---|---|---|---|
| **App Service Plan** | P1v3 (2 cores, 8GB RAM) x2 | 2 instances | $214/mo each | **$428** |
| **Azure Cosmos DB** | Autoscale (400-4000 RU/s) | ~2000 RU/s avg | $0.012/RU/s/hr | **$175** |
| **Azure Storage** | Standard LRS | 100 GB + 1M ops | $0.02/GB + ops | **$3** |
| **Azure AI Search** | Basic (2GB storage, 50K docs) | 1 replica, 1 partition | $75/mo | **$75** |
| **Azure Function App** | Premium EP1 (no cold start) | 1 instance | $165/mo | **$165** |
| **Application Insights** | Pay-as-you-go | 20 GB logs/mo | $2.30/GB (after 5GB) | **$35** |
| **Azure Front Door** | Standard tier (optional) | 100 GB egress | $35 base + $0.01/GB | **$40** |
| **Azure Key Vault** | Standard | 10K operations | $0.03/10K ops | **$1** |
| **Bandwidth** | Outbound (Zone 1) | 500 GB/mo | $0.05/GB (after 100GB) | **$20** |

**Total Production Cost**: ~**$970/month** (~$11,600/year)

---

## Cost Optimization Strategies

### 1. Cosmos DB Optimization

**Problem**: Cosmos DB thường là service đắt nhất (~40% budget).

**Solutions**:

#### a) Use Serverless for Low Traffic
```
# Development/staging: Serverless (pay per request)
# Vào Cosmos DB → Create account → chọn Serverless capacity mode
# Good for < 10M RU/month
```

#### b) Optimize Queries (Reduce RU Consumption)
```python
# ❌ Bad: Cross-partition query (expensive)
query = "SELECT * FROM c WHERE c.title LIKE '%tai nghe%'"

# ✓ Good: Partition-scoped query
query = "SELECT * FROM c WHERE c.shop_id = @shop_id AND c.title LIKE '%tai nghe%'"
```

#### c) Use Indexing Policy to Exclude Unused Fields
```json
{
  "indexingMode": "consistent",
  "automatic": true,
  "includedPaths": [
    {"path": "/title/?"},
    {"path": "/status/?"},
    {"path": "/created_at/?"}
  ],
  "excludedPaths": [
    {"path": "/thumbnail_url/?"},
    {"path": "/thumbnail_original/?"}
  ]
}
```

**Savings**: 20-30% RU reduction

#### d) Archive Old Data
```python
# Move links > 6 months to cheaper storage
old_links = CosmosDBService.query(
    'links',
    'SELECT * FROM c WHERE c.created_at < @cutoff AND c.status = "done"'
)
# Export to Azure Table Storage ($0.0005/GB vs Cosmos $0.25/GB)
```

**Savings**: ~$50/month for 100GB archived data

---

### 2. Azure Search Optimization

**Free Tier Limits**:
- 50 MB storage
- 3 indexes max
- 10,000 documents

**Upgrade trigger**: Khi vượt 10K products.

**Optimization**:
```python
# Chỉ index active products
products = [p for p in products if p['status'] == 'active']

# Không index thumbnail URLs (dùng Cosmos làm source of truth)
document = {
    'id': product['id'],
    'title': product['title'],
    'title_vector': vector,
    # Remove: 'thumbnail_url', 'original_url' (save space)
}
```

**Savings**: Delay upgrade từ Free → Basic ($75/mo) thêm 3-6 tháng.

---

### 3. App Service Plan Optimization

**Development**:
- Use **B1** ($13/mo) thay vì B2 ($70/mo) nếu traffic thấp
- Stop app service ngoài giờ làm việc (schedule):
```bash
# Auto-stop ngoài giờ làm việc:
```

**Production**:
- Use **P1v3** thay vì P1v2 (same price, better CPU)
- Auto-scale based on CPU:
```
# Vào App Service Plan → Scale out (App Service plan) → chọn Custom autoscale
# Set rule: CPU > 70% → add 1 instance, CPU < 40% → remove 1 instance
```

**Savings**: $200/month (chỉ scale khi cần)

---

### 4. Storage Cost Optimization

**Lifecycle Management**: Tự động chuyển thumbnails sang Cool tier sau 30 ngày.

```json
{
  "rules": [
    {
      "name": "move-to-cool",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "tierToCool": {"daysAfterModificationGreaterThan": 30},
            "tierToArchive": {"daysAfterModificationGreaterThan": 180}
          }
        },
        "filters": {"blobTypes": ["blockBlob"]}
      }
    }
  ]
}
```

**Cost comparison**:
- Hot tier: $0.02/GB
- Cool tier: $0.01/GB (50% cheaper, slower access)
- Archive tier: $0.002/GB (90% cheaper, retrieval fee)

**Savings**: $1-2/month per 100GB

---

### 5. Function App Optimization

**Consumption Plan** (pay-per-execution):
- First 1M executions free
- $0.20 per 1M executions after
- Good for < 10M executions/month

**Premium Plan** ($165/mo):
- No cold start
- Predictable cost
- Good for > 20M executions/month

**For this project**: Consumption plan đủ (< 1M scraping jobs/month).

**Optimization**:
```python
# Reduce execution time = reduce cost
# Bad: Scrape entire page (30s)
# Good: Scrape chỉ title + thumbnail (5s) - 6x nhanh hơn
```

---

### 6. Application Insights Cost Control

**Free tier**: 5 GB/month

**Exceed triggers**: $2.30/GB

**Optimization**:

#### a) Sampling
```python
# config/settings/production.py
OPENCENSUS = {
    'TRACE': {
        'SAMPLER': 'opencensus.trace.samplers.ProbabilitySampler(rate=0.1)',  # 10% sampling
    }
}
```

#### b) Filter Verbose Logs
```python
LOGGING = {
    'loggers': {
        'django': {
            'level': 'WARNING',  # Chỉ log warning+ (không log INFO)
        },
    }
}
```

#### c) Set Retention to 90 Days
```
# Vào Application Insights → Usage and estimated costs → Data retention → chọn 90 days
```

**Savings**: $20-30/month bằng cách giữ logs < 10GB

---

## Reserved Instances (RI) Savings

**Nếu commit 1-3 năm**, tiết kiệm 30-70%:

| Service | Pay-as-you-go | 1-year RI | 3-year RI | Savings |
|---|---|---|---|---|
| P1v3 App Service | $214/mo | $150/mo | $107/mo | 50% |
| Cosmos DB (100 RU/s) | $9/mo | $6/mo | $4/mo | 55% |

**Recommendation**: Chỉ mua RI sau 3-6 tháng vận hành (khi traffic stable).

---

## Budget Alerts

**Setup alerts** để tránh cost overrun:

```bash
# Alert khi cost > $1000/month
# Vào Cost Management + Billing → Budgets → + Add
# Set amount: $1000, time grain: Monthly, alert khi > 80%
```

**Thresholds**:
- 50% → Info email
- 80% → Warning email
- 100% → Critical alert + investigate

---

## Cost Monitoring Dashboard

**Azure Cost Management + Billing**:

1. **Cost by Service** (pie chart):
   - Cosmos DB: 40%
   - App Service: 35%
   - AI Search: 10%
   - Others: 15%

2. **Cost Trend** (line chart):
   - Daily cost
   - 7-day moving average
   - Budget threshold line

3. **Top Cost Contributors** (table):
   - Cosmos DB container: `products` ($120/mo)
   - App Service instance: `app-shopee-aff-prod-1` ($214/mo)

**Query sample** (Kusto - Cost Management):
```kusto
// Top 10 expensive resources last 30 days
AzureDiagnostics
| where TimeGenerated > ago(30d)
| summarize TotalCost = sum(todouble(Cost)) by ResourceId
| top 10 by TotalCost desc
```

---

## Free Tier Maximization (Hobbyist/MVP)

**Goal**: Run system với < $20/month.

| Service | Free Tier | Upgrade Trigger |
|---|---|---|
| App Service | F1 (1GB RAM, 1hr/day) | Always-on needed |
| Cosmos DB | 1000 RU/s free forever | > 10M RU/month |
| Azure Functions | 1M executions/mo | > 1M scrapes/mo |
| AI Search | Free (50MB, 3 indexes) | > 10K products |
| Storage | First 5GB free | > 5GB thumbnails |
| App Insights | 5GB logs free | > 5GB/month |

**Workaround for F1 App Service** (1hr/day limit):
- Deploy to **Azure Container Instances** ($0.0125/vCore/hr):
  ```bash
  # Run 24/7: 730 hours/mo x 1 vCore x $0.0125 = $9/mo
  # Vào Container Instances → + Create → chọn image từ ACR
  ```

**Total Free/Cheap Setup**: ~$15/month (good cho MVP hoặc personal project)

---

## Cost Comparison vs Alternatives

### Self-hosted (Azure VM)

| Component | Azure Managed | Self-hosted VM |
|---|---|---|
| Web app | $214/mo (P1v3) | $70/mo (B2s VM) |
| Database | $175/mo (Cosmos) | $0 (PostgreSQL) |
| Search | $75/mo (AI Search) | $0 (Elasticsearch) |
| Function | $0 (Consumption) | Included in VM |
| **Total** | **$464/mo** | **$70/mo** |
| Maintenance effort | Low (managed) | High (manual) |

**Trade-off**: Tiết kiệm $400/month nhưng cần quản lý server, backup, security patches.

---

### AWS/GCP Equivalent

**AWS**:
- EC2 (t3.medium): $30/mo
- DynamoDB: $25/mo (on-demand)
- OpenSearch: $50/mo
- Lambda: $0 (< 1M invocations)
- **Total**: ~$105/mo

**GCP**:
- Cloud Run: $20/mo
- Firestore: $30/mo
- Vertex AI Search: $60/mo
- Cloud Functions: $0
- **Total**: ~$110/mo

**Verdict**: Azure đắt hơn ~10-20% nhưng tích hợp Azure AI Search semantic search tốt hơn.

---

## Long-term Cost Projection

**Year 1** (gradual growth):
- Month 1-3: $80/mo (dev environment)
- Month 4-6: $200/mo (soft launch, basic tier)
- Month 7-12: $500/mo (production, 5K users)

**Year 2** (scale up):
- Month 13-24: $1000/mo (10K users, full features)

**Year 3+** (optimize):
- Reserved Instances: -40% → $600/mo
- Caching layer (Redis): +$50/mo
- CDN for images: +$30/mo
- **Net**: ~$680/mo

**5-year TCO**: ~$50,000 (cloud) vs $15,000 (self-hosted) + DevOps salary.

---

## Action Items

- [ ] Enable Azure Cost Management alerts
- [ ] Review costs weekly (first 3 months)
- [ ] Set up tagging strategy (env:dev, env:prod, project:shopee-aff)
- [ ] Implement Application Insights sampling in production
- [ ] Archive old Cosmos DB data to cheap storage (after 6 months)
- [ ] Consider Reserved Instances after usage pattern stabilizes
- [ ] Monitor Azure AI Search query usage with custom dashboard
- [ ] Evaluate serverless Cosmos DB for dev/staging environments
