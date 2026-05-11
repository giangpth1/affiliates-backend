# Azure Function App - Deployment Guide with Playwright

## 📝 Prerequisites

- Azure Student Account
- Azure CLI installed
- Azure subscription ID

## 🚀 Quick Deployment

### 1. Install Playwright in Function App (Important!)

Function App cần install Playwright browsers sau khi deploy. Tạo startup command:

**File**: `azure_functions/.platform/startup.sh`
```bash
#!/bin/bash
python -m playwright install chromium
```

### 2. Deploy Function App

```powershell
# Login to Azure
az login

# Set subscription (Student)
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Create resource group (if not exists)
az group create --name rg-shopee-aff --location southeastasia

# Create storage account (for Function App)
az storage account create \
  --name stfuncshopeeaff \
  --resource-group rg-shopee-aff \
  --location southeastasia \
  --sku Standard_LRS

# Create Function App (Consumption Plan - FREE!)
az functionapp create \
  --resource-group rg-shopee-aff \
  --name func-shopee-scraper \
  --storage-account stfuncshopeeaff \
  --consumption-plan-location southeastasia \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux

# Configure app settings (environment variables)
az functionapp config appsettings set \
  --name func-shopee-scraper \
  --resource-group rg-shopee-aff \
  --settings \
    "COSMOS_DB_URL=YOUR_COSMOS_URL" \
    "COSMOS_DB_KEY=YOUR_COSMOS_KEY" \
    "COSMOS_DB_DATABASE=shopee-aff-db" \
    "AZURE_STORAGE_CONNECTION_STRING=YOUR_STORAGE_CONN" \
    "AZURE_STORAGE_CONTAINER=thumbnails" \
    "AZURE_SEARCH_ENDPOINT=YOUR_SEARCH_ENDPOINT" \
    "AZURE_SEARCH_KEY=YOUR_SEARCH_KEY" \
    "AZURE_SEARCH_INDEX=idx-shopee-aff-management" \
    "PLAYWRIGHT_BROWSERS_PATH=/tmp/ms-playwright"

# Deploy code
cd azure_functions
func azure functionapp publish func-shopee-scraper --python

# Install Playwright browsers (CRITICAL!)
az functionapp config set \
  --name func-shopee-scraper \
  --resource-group rg-shopee-aff \
  --startup-file "python -m playwright install chromium"
```

### 3. Get Function App URL & Key

```powershell
# Get URL
az functionapp show \
  --name func-shopee-scraper \
  --resource-group rg-shopee-aff \
  --query "defaultHostName" -o tsv

# Get function key
az functionapp function keys list \
  --name func-shopee-scraper \
  --resource-group rg-shopee-aff \
  --function-name scrape_product \
  --query "default" -o tsv
```

### 4. Update Backend .env

```bash
# backend/.env
FUNCTION_APP_URL=https://func-shopee-scraper.azurewebsites.net
FUNCTION_APP_KEY=YOUR_FUNCTION_KEY_FROM_STEP_3
ASYNC_LINK_PROCESSING=True
```

---

## 🔧 Alternative: Deploy with Azure Portal

### Step 1: Create Function App
1. Go to [Azure Portal](https://portal.azure.com)
2. Create Resource → Function App
3. Settings:
   - **Resource Group**: rg-shopee-aff
   - **Name**: func-shopee-scraper
   - **Runtime**: Python 3.11
   - **Region**: Southeast Asia
   - **Plan**: Consumption (Serverless)
   - **Storage**: Create new (stfuncshopeeaff)

### Step 2: Configure Settings
1. Function App → Configuration → Application settings
2. Add all environment variables (COSMOS_DB_URL, etc.)
3. Save

### Step 3: Deploy Code
Option A: VS Code Extension
- Install "Azure Functions" extension
- Right-click `azure_functions` folder → Deploy to Function App

Option B: ZIP Deploy
```powershell
cd azure_functions
Compress-Archive -Path * -DestinationPath deploy.zip
az functionapp deployment source config-zip \
  --name func-shopee-scraper \
  --resource-group rg-shopee-aff \
  --src deploy.zip
```

### Step 4: Install Playwright
```powershell
# SSH into Function App (Advanced Tools → SSH)
python -m playwright install chromium
```

---

## ✅ Verification

### Test Function App

```powershell
# Test endpoint
$url = "https://func-shopee-scraper.azurewebsites.net/api/scrape_product"
$key = "YOUR_FUNCTION_KEY"
$body = @{
    link_id = "test-123"
    url = "https://s.shopee.vn/7KteAH4OUm"
} | ConvertTo-Json

Invoke-RestMethod -Uri $url -Method Post -Body $body -Headers @{
    "Content-Type" = "application/json"
    "x-functions-key" = $key
}
```

Expected response:
```json
{
  "status": "done",
  "product_id": "uuid"
}
```

### Monitor Logs

```powershell
# Stream logs
az functionapp log tail \
  --name func-shopee-scraper \
  --resource-group rg-shopee-aff
```

Or in Azure Portal:
- Function App → Monitor → Logs

---

## 💰 Cost Estimate (Student Free Tier)

### Monthly Usage: 1000 links

**Function App Consumption**:
- Execution time: 10s/link
- Memory: 1.5GB
- GB-s: 1000 × 10 × 1.5 = 15,000 GB-s
- **Cost**: $0 (Free tier: 400,000 GB-s/month)

**Storage (function files)**:
- ~50MB
- **Cost**: $0 (negligible)

**Total**: **$0/month** ✅

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'playwright'"

**Solution**: Rebuild with requirements.txt
```powershell
cd azure_functions
pip install -r requirements.txt --target .python_packages/lib/site-packages
func azure functionapp publish func-shopee-scraper --python
```

### Issue: "Playwright browsers not found"

**Solution**: Install browsers post-deployment
```bash
# SSH to Function App
python -m playwright install chromium
```

Or add to startup command:
```bash
az functionapp config set \
  --name func-shopee-scraper \
  --resource-group rg-shopee-aff \
  --startup-file "python -m playwright install chromium && python -m azure.functions.worker"
```

### Issue: Function timeout (default 5 min)

**Solution**: Increase timeout
```powershell
# Update host.json
{
  "functionTimeout": "00:10:00"  // 10 minutes
}
```

### Issue: High memory usage

**Solution**: Upgrade plan (if needed)
- Consumption: 1.5GB max
- Premium EP1: 3.5GB (~$150/month)

For Student tier, Consumption should be enough!

---

## 📊 Monitoring

### Application Insights

Enable Application Insights for detailed monitoring:

```powershell
# Create App Insights
az monitor app-insights component create \
  --app func-shopee-insights \
  --location southeastasia \
  --resource-group rg-shopee-aff \
  --application-type web

# Link to Function App
az functionapp config appsettings set \
  --name func-shopee-scraper \
  --resource-group rg-shopee-aff \
  --settings "APPINSIGHTS_INSTRUMENTATIONKEY=YOUR_KEY"
```

View metrics:
- Azure Portal → Application Insights → Metrics
- Monitor execution time, failures, dependencies

---

## 🔐 Security

### Function Keys

- **Master Key**: Full access (keep secret!)
- **Function Key**: Per-function access (use in backend .env)

Get keys:
```powershell
# List all keys
az functionapp function keys list \
  --name func-shopee-scraper \
  --resource-group rg-shopee-aff \
  --function-name scrape_product
```

### Best Practices

1. ✅ Store keys in Azure Key Vault (production)
2. ✅ Enable HTTPS only
3. ✅ Restrict CORS (add Django backend URL)
4. ✅ Use Managed Identity (future upgrade)

---

## 🎯 Next Steps

1. Deploy Function App ✅
2. Update backend `.env` with Function URL & Key
3. Test link creation from frontend
4. Monitor logs and performance
5. Scale automatically with usage!

---

**Deployment Time**: ~15-20 minutes
**Monthly Cost**: $0 (Student Free Tier)
**Scalability**: 0 → 200 instances automatically

🚀 Ready to deploy? Let me know if you need help with any step!
