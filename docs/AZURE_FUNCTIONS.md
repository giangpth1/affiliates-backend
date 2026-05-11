# Azure Functions - Implementation Guide

**Last Updated**: 2026-05-08  
**Status**: ✅ Ready to Deploy

---

## 📋 Overview

Azure Function App cho async scraping Shopee products. Được trigger từ Django backend khi user tạo affiliate link mới.

## 🏗️ Architecture

```
Django Backend (API)
    │
    │ POST /api/links/ (create link)
    │
    ├──> Response 201 (link status: "pending")
    │
    └──> Async call Azure Function
            │
            ├──> 1. Update link status → "processing"
            ├──> 2. Resolve redirect (shp.ee → full URL)
            ├──> 3. Scrape Shopee page (title, price, thumbnail)
            ├──> 4. Upload thumbnail → Blob Storage
            ├──> 5. Create product → Cosmos DB
            ├──> 6. Index product → AI Search
            └──> 7. Update link → "done" (with product_id)
```

## 📁 Files Created

| File | Purpose | Status |
|------|---------|--------|
| `host.json` | Function App config (timeout, logging) | ✅ Created |
| `requirements.txt` | Python dependencies | ✅ Created |
| `local.settings.json.example` | Template for env vars | ✅ Created |
| `local.settings.json` | Actual env vars (gitignored) | ✅ Created |
| `.funcignore` | Deploy exclusion rules | ✅ Created |
| `README.md` | Setup & testing guide | ✅ Created |
| `DEPLOY.md` | Quick deploy guide (Azure CLI) | ✅ Created |
| `scrape_product/__init__.py` | Main handler logic | ✅ Existing |
| `scrape_product/function.json` | Function binding config | ✅ Existing |

## 🚀 Deployment Options

### Option 1: Azure Portal (Manual)

**Pros**: Visual, beginner-friendly  
**Cons**: Slower, manual config

1. Portal → Create Function App
2. Copy/paste env vars
3. Deploy via VS Code extension or `func` CLI

**Guide**: See [README.md](../azure_functions/README.md)

---

### Option 2: Azure CLI (Recommended)

**Pros**: Fast, reproducible, scriptable  
**Cons**: Requires CLI installed

```powershell
# 1. Create resources
az functionapp create --name func-shopee-aff-dev ...

# 2. Set env vars
az functionapp config appsettings set ...

# 3. Deploy code
cd azure_functions
func azure functionapp publish func-shopee-aff-dev --python
```

**Guide**: See [DEPLOY.md](../azure_functions/DEPLOY.md)

---

### Option 3: Bicep/ARM Template (Future)

**Pros**: IaC, version controlled, CI/CD ready  
**Cons**: Requires Bicep knowledge

```bicep
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: 'func-shopee-aff-dev'
  location: location
  kind: 'functionapp,linux'
  // ...
}
```

**Status**: ⏳ Planned for Phase 6 (Deploy)

## 🔐 Required Environment Variables

| Variable | Example | Where to Get |
|----------|---------|--------------|
| `COSMOS_DB_URL` | `https://cosmos-xxx.documents.azure.com:443/` | Cosmos DB → Overview → URI |
| `COSMOS_DB_KEY` | `abc123...` | Cosmos DB → Keys → Primary Key |
| `COSMOS_DB_DATABASE` | `shopee-aff-db` | Database name |
| `AZURE_STORAGE_CONNECTION_STRING` | `DefaultEndpointsProtocol=https;...` | Storage Account → Access Keys |
| `AZURE_STORAGE_CONTAINER` | `product-thumbnails` | Container name |
| `AZURE_SEARCH_ENDPOINT` | `https://search-xxx.search.windows.net` | AI Search → Overview → URL |
| `AZURE_SEARCH_KEY` | `xyz789...` | AI Search → Keys → Primary admin key |
| `AZURE_SEARCH_INDEX` | `products` | Index name |

## 📊 Function Spec

### Input (HTTP POST)

```json
{
  "link_id": "uuid-of-link-record",
  "url": "https://shp.ee/abc123"
}
```

### Output (Success)

```json
{
  "status": "done",
  "product_id": "uuid-of-created-product"
}
```

### Output (Error)

**HTTP 400 Bad Request**:
```
Bad request: 'link_id'
```

**HTTP 500 Internal Server Error**:
```
Scraping failed: Connection timeout
```

## 🧪 Testing

### Local Testing

```powershell
# 1. Setup
cd azure_functions
pip install -r requirements.txt
cp local.settings.json.example local.settings.json
# Edit local.settings.json with real Azure credentials

# 2. Run function host
func start

# 3. Test
curl -X POST http://localhost:7071/api/scrape_product `
  -H "Content-Type: application/json" `
  -d '{\"link_id\":\"test-123\",\"url\":\"https://shp.ee/abc\"}'
```

### Production Testing

```powershell
$url = "https://func-shopee-aff-dev.azurewebsites.net/api/scrape_product?code=<key>"
Invoke-RestMethod -Uri $url -Method POST -Body '{"link_id":"test","url":"https://shp.ee/abc"}' -ContentType "application/json"
```

## 📈 Monitoring

### Application Insights (Recommended)

```kql
traces
| where message contains "Scraping"
| project timestamp, message, severityLevel
| order by timestamp desc
| take 100
```

### Real-time Logs

```powershell
func azure functionapp logstream func-shopee-aff-dev
```

### Metrics to Track

- **Invocations**: Total scrape requests
- **Success Rate**: done / total
- **Duration**: p50, p95, p99 latency
- **Errors**: 4xx, 5xx by error type
- **RU Consumption**: Cosmos DB cost per scrape

## 💰 Cost

### Consumption Plan (Dev/Staging)

- First 1M executions/month: **FREE**
- After: $0.20 per 1M executions
- Estimate (50K scrapes/month): **$0**

### Premium Plan (Production)

- EP1: 1 vCore, 3.5GB RAM
- **$165/month** (no cold start, always warm)
- Use case: Need <1s response time

### Cost Optimization Tips

1. **Batch scraping**: Queue multiple links, process in batches
2. **Cache products**: Check if product exists before re-scraping
3. **Timeout**: Set reasonable timeout (don't wait 5 min for slow sites)
4. **Retry logic**: Exponential backoff for transient failures

## 🔧 Troubleshooting

### "ModuleNotFoundError: azure.functions"

**Cause**: Dependencies not installed on Azure  
**Fix**:
```powershell
func azure functionapp publish func-shopee-aff-dev --build remote
```

### "KeyError: 'COSMOS_DB_URL'"

**Cause**: Missing environment variable  
**Fix**:
```powershell
az functionapp config appsettings list --name func-shopee-aff-dev --resource-group rg-shopee-aff-dev
# Verify all vars are set
```

### "Cold start > 10 seconds"

**Cause**: Consumption Plan cold start  
**Fix**:
- Upgrade to Premium Plan (EP1) for instant response
- Or accept cold start (only first request after idle)

### "Scraping timeout"

**Cause**: Shopee blocking or slow response  
**Fix**:
- Add User-Agent rotation
- Implement retry with exponential backoff
- Set reasonable timeout (20s max)

## 🔄 Update Workflow

1. Edit code in `azure_functions/scrape_product/__init__.py`
2. Test locally: `func start`
3. Deploy: `func azure functionapp publish func-shopee-aff-dev`
4. Verify logs: `func azure functionapp logstream ...`

## ✅ Deployment Checklist

- [ ] Azure Function App created
- [ ] All env vars configured
- [ ] Code deployed successfully
- [ ] Function key obtained
- [ ] Backend `.env` updated with function URL & key
- [ ] Application Insights enabled
- [ ] Test scraping with real Shopee link
- [ ] Monitor logs for errors
- [ ] Set budget alert (if Consumption Plan)

## 📝 Next Steps

1. **Deploy Function App** (see [DEPLOY.md](../azure_functions/DEPLOY.md))
2. **Update Django backend** to call function when creating links
3. **Test end-to-end**: Web/Mobile → API → Function → Cosmos DB
4. **Monitor performance** via Application Insights
5. **Optimize**: Cache, batch, retry logic

---

**Questions?** Check [README.md](../azure_functions/README.md) or deployment logs.
