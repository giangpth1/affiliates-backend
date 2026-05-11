"""Run once: python scripts/create_search_index.py"""
import os, sys
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'apps'))
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

index_name = settings.AZURE_SEARCH_INDEX

try:
    client.delete_index(index_name)
    print(f"Deleted existing index '{index_name}'")
except Exception:
    pass

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
    name=index_name,
    fields=fields,
    semantic_search=SemanticSearch(configurations=[semantic_config])
)

result = client.create_or_update_index(index)
print(f"✓ Index '{result.name}' created/updated with {len(result.fields)} fields")
