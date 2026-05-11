---
title: Phase 3 — AI Search Integration
version: 2.0.0
updated: 2026-05-07
---

# Phase 3: AI Search Integration

## Goals
- Azure AI Search index với semantic configuration
- Auto-index sản phẩm khi tạo mới
- Semantic search dùng built-in ML của Azure AI Search (không cần embedding)
- Search API trả kết quả xếp hạng theo ngữ nghĩa

> **Azure AI Search Semantic Search** dùng ML models built-in của Microsoft để hiểu ngữ nghĩa query và re-rank kết quả. Không cần Azure OpenAI hay embedding model riêng. Yêu cầu **Basic tier** trở lên.

---

## Step 3.1 — Azure AI Search Index Schema

### 3.1.1 Tạo Index

Chạy script này **một lần** để tạo index với vector fields:

**`scripts/create_search_index.py`**:
```python
"""Run once: python scripts/create_search_index.py"""
import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
django.setup()

from django.conf import settings
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    SemanticConfiguration,
    SemanticSearch,
    SemanticPrioritizedFields,
    SemanticField,
)
from azure.core.credentials import AzureKeyCredential

client = SearchIndexClient(
    endpoint=settings.AZURE_SEARCH_ENDPOINT,
    credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY)
)

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
    SearchableField(name="title", type=SearchFieldDataType.String, analyzer_name="vi.microsoft"),
    SearchableField(name="category", type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="shop_id", type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="item_id", type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="thumbnail_url", type=SearchFieldDataType.String),
    SimpleField(name="original_url", type=SearchFieldDataType.String),
    SimpleField(name="price", type=SearchFieldDataType.Double, filterable=True, sortable=True),
    SimpleField(name="price_currency", type=SearchFieldDataType.String),
    SimpleField(name="created_at", type=SearchFieldDataType.String, sortable=True),
]

semantic_config = SemanticConfiguration(
    name="semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="title"),
        content_fields=[SemanticField(field_name="category")]
    )
)

index = SearchIndex(
    name=settings.AZURE_SEARCH_INDEX,
    fields=fields,
    semantic_search=SemanticSearch(configurations=[semantic_config])
)

result = client.create_or_update_index(index)
print(f"✓ Index '{result.name}' created/updated with {len(result.fields)} fields")
```

```powershell
cd backend
python scripts/create_search_index.py
```

---

## Step 3.2 — Azure Search Service

**`services/azure_search.py`**:
```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

_search_client = None


def get_search_client() -> SearchClient:
    global _search_client
    if _search_client is None:
        _search_client = SearchClient(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            index_name=settings.AZURE_SEARCH_INDEX,
            credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY)
        )
    return _search_client


class AzureSearchService:

    @staticmethod
    def index_product(product: dict) -> None:
        """Index a product document."""
        client = get_search_client()

        document = {
            'id': product['id'],
            'title': product.get('title', ''),
            'category': product.get('category', ''),
            'shop_id': product.get('shop_id', ''),
            'item_id': product.get('item_id', ''),
            'thumbnail_url': product.get('thumbnail_url', ''),
            'original_url': product.get('original_url', ''),
            'price': product.get('price'),
            'price_currency': product.get('price_currency', 'VND'),
            'created_at': product.get('created_at', ''),
        }

        result = client.upload_documents(documents=[document])
        if not result[0].succeeded:
            logger.error(f"Failed to index product {product['id']}: {result[0].errors}")

    @staticmethod
    def index_products_batch(products: list[dict]) -> None:
        """Index multiple products."""
        if not products:
            return

        documents = []
        for product in products:
            documents.append({
                'id': product['id'],
                'title': product.get('title', ''),
                'category': product.get('category', ''),
                'shop_id': product.get('shop_id', ''),
                'item_id': product.get('item_id', ''),
                'thumbnail_url': product.get('thumbnail_url', ''),
                'original_url': product.get('original_url', ''),
                'price': product.get('price'),
                'price_currency': product.get('price_currency', 'VND'),
                'created_at': product.get('created_at', ''),
            })

        client = get_search_client()
        client.upload_documents(documents=documents)

    @staticmethod
    def semantic_search(
        query: str,
        top: int = 10,
        min_price: float = None,
        max_price: float = None,
    ) -> list[dict]:
        """
        Semantic search using Azure AI Search built-in ML models.
        Returns ranked list of product dicts.
        """
        client = get_search_client()

        filters = []
        if min_price is not None:
            filters.append(f"price ge {min_price}")
        if max_price is not None:
            filters.append(f"price le {max_price}")
        filter_str = " and ".join(filters) if filters else None

        results = client.search(
            search_text=query,
            filter=filter_str,
            query_type="semantic",
            semantic_configuration_name="semantic-config",
            top=top,
            select=["id", "title", "thumbnail_url", "original_url", "price", "price_currency", "shop_id", "created_at"],
            highlight_fields="title",
        )

        output = []
        for result in results:
            item = dict(result)
            item['score'] = result['@search.score']
            item['highlights'] = result.get('@search.highlights', {})
            output.append(item)

        return output

    @staticmethod
    def delete_product(product_id: str) -> None:
        client = get_search_client()
        client.delete_documents(documents=[{'id': product_id}])
```

---

## Step 3.4 — Auto-Index on Product Creation

Cập nhật `apps/products/services.py` — thêm indexing sau khi tạo product:

```python
# Thêm vào cuối ProductService.create():
from services.azure_search import AzureSearchService

@staticmethod
def create(data: dict) -> dict:
    product = Product(**data)
    saved = CosmosDBService.upsert(CONTAINER, product.to_dict())
    
    # Auto-index in Azure AI Search
    try:
        AzureSearchService.index_product(saved)
    except Exception as e:
        logger.warning(f"Failed to index product {saved['id']}: {e}")
    
    return saved
```

Cập nhật Azure Function `scrape_product/__init__.py` — thêm indexing step:

```python
# Sau khi save product vào Cosmos DB, thêm:
# 5b. Index in Azure AI Search
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

SEARCH_ENDPOINT = os.environ['AZURE_SEARCH_ENDPOINT']
SEARCH_KEY = os.environ['AZURE_SEARCH_KEY']
SEARCH_INDEX = os.environ['AZURE_SEARCH_INDEX']

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=SEARCH_INDEX,
    credential=AzureKeyCredential(SEARCH_KEY)
)
search_client.upload_documents(documents=[product])
```

---

## Step 3.5 — Search App (Django)

### 3.5.1 Search Views

**`apps/search/views.py`**:
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.azure_search import AzureSearchService
from apps.search.serializers import SearchQuerySerializer, SearchResultSerializer


class SmartSearchView(APIView):
    """
    GET /api/search/?q=tai+nghe+sony&top=10&min_price=100000&max_price=5000000
    """

    def get(self, request):
        serializer = SearchQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        results = AzureSearchService.semantic_search(
            query=serializer.validated_data['q'],
            top=serializer.validated_data.get('top', 10),
            min_price=serializer.validated_data.get('min_price'),
            max_price=serializer.validated_data.get('max_price'),
        )

        return Response({
            'query': serializer.validated_data['q'],
            'count': len(results),
            'results': SearchResultSerializer(results, many=True).data
        })
```

### 3.5.2 Search Serializers

**`apps/search/serializers.py`**:
```python
from rest_framework import serializers


class SearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(min_length=1, max_length=200)
    top = serializers.IntegerField(min_value=1, max_value=50, default=10, required=False)
    min_price = serializers.FloatField(required=False, allow_null=True)
    max_price = serializers.FloatField(required=False, allow_null=True)


class SearchResultSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    thumbnail_url = serializers.CharField()
    original_url = serializers.CharField()
    price = serializers.FloatField(allow_null=True)
    price_currency = serializers.CharField()
    score = serializers.FloatField()
    highlights = serializers.DictField(required=False)
```

### 3.5.3 Search URLs

**`apps/search/urls.py`**:
```python
from django.urls import path
from .views import SmartSearchView

urlpatterns = [
    path('', SmartSearchView.as_view(), name='smart-search'),
]
```

---

## Step 3.6 — Bulk Re-index Script

Dùng khi cần sync lại toàn bộ products từ Cosmos DB vào Search:

**`scripts/reindex_all.py`**:
```python
"""Reindex all products from Cosmos DB into Azure AI Search."""
import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
django.setup()

from services.cosmos_db import CosmosDBService
from services.azure_search import AzureSearchService

BATCH_SIZE = 100

def main():
    query = "SELECT * FROM c WHERE c.status = 'active'"
    products = CosmosDBService.query('products', query)
    print(f"Found {len(products)} products to index")

    for i in range(0, len(products), BATCH_SIZE):
        batch = products[i:i + BATCH_SIZE]
        AzureSearchService.index_products_batch(batch)
        print(f"Indexed {min(i + BATCH_SIZE, len(products))}/{len(products)}")

    print("✓ Reindex complete")

if __name__ == '__main__':
    main()
```

---

## Step 3.7 — Manual Search Test

```powershell
# Test via curl (hoặc REST Client trong VS Code)
curl "http://localhost:8000/api/search/?q=tai+nghe+sony&top=5"

# Expected response:
# {
#   "query": "tai nghe sony",
#   "count": 3,
#   "results": [
#     {
#       "id": "...",
#       "title": "Tai nghe Sony WH-1000XM5",
#       "thumbnail_url": "https://stshopeeaffdev.blob.core.windows.net/...",
#       "score": 0.934,
#       "highlights": {"title": ["<em>Tai nghe Sony</em> WH-1000XM5"]}
#     }
#   ]
# }
```

---

## Phase 3 Checklist

- [ ] Search index tạo thành công với semantic config (`python scripts/create_search_index.py`)
- [ ] `services/azure_search.py` — `semantic_search()` trả kết quả đúng thứ tự
- [ ] Product auto-index khi tạo mới (trong `ProductService.create`)
- [ ] Azure Function cũng index sau khi scrape
- [ ] `apps/search/` — views, serializers, urls hoàn chỉnh
- [ ] `scripts/reindex_all.py` chạy thành công
- [ ] Manual test: search "tai nghe" → sản phẩm đúng ở top
- [ ] Manual test: search với filter giá → chỉ hiện sản phẩm trong khoảng

**Next:** [Phase 4 — Flutter Mobile App](PLAN_PHASE_4_MOBILE.md)
