"""Reindex all products from Cosmos DB into Azure AI Search."""
import os, sys
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'apps'))
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
