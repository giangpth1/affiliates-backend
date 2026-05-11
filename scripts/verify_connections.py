"""Verify all Azure service connections."""
import os, sys
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'apps'))
django.setup()

from django.conf import settings

CHECKS = []

def check(name, ok, detail=''):
    CHECKS.append((name, ok, detail))
    status = '✓' if ok else '✗'
    print(f"  {status} {name}{' — ' + detail if detail else ''}")

print("Verifying Azure connections...\n")

# Django
check('Django settings loaded', settings.SECRET_KEY is not None)

# Cosmos DB
try:
    from azure.cosmos import CosmosClient
    if settings.COSMOS_DB_URL and settings.COSMOS_DB_KEY:
        client = CosmosClient(settings.COSMOS_DB_URL, credential=settings.COSMOS_DB_KEY)
        db = client.get_database_client(settings.COSMOS_DB_DATABASE)
        db.read()
        check('Cosmos DB', True, settings.COSMOS_DB_DATABASE)
    else:
        check('Cosmos DB', False, 'COSMOS_DB_URL/KEY not configured')
except Exception as e:
    check('Cosmos DB', False, str(e))

# Storage
try:
    from azure.storage.blob import BlobServiceClient
    if settings.AZURE_STORAGE_CONNECTION_STRING:
        blob = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        blob.get_account_information()
        check('Azure Storage', True)
    else:
        check('Azure Storage', False, 'AZURE_STORAGE_CONNECTION_STRING not configured')
except Exception as e:
    check('Azure Storage', False, str(e))

# AI Search
try:
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    if settings.AZURE_SEARCH_ENDPOINT and settings.AZURE_SEARCH_KEY:
        client = SearchClient(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            index_name=settings.AZURE_SEARCH_INDEX,
            credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY)
        )
        client.get_document_count()
        check('Azure AI Search', True, settings.AZURE_SEARCH_INDEX)
    else:
        check('Azure AI Search', False, 'AZURE_SEARCH_ENDPOINT/KEY not configured')
except Exception as e:
    check('Azure AI Search', False, str(e))

print(f"\nResults: {sum(1 for _, ok, _ in CHECKS if ok)}/{len(CHECKS)} checks passed")

if all(ok for _, ok, _ in CHECKS):
    print("All connections verified!")
else:
    failed = [name for name, ok, _ in CHECKS if not ok]
    print(f"Failed: {', '.join(failed)}")
    print("Run Azure provisioning scripts or check .env configuration.")
