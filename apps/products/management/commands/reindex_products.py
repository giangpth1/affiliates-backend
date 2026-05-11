from django.core.management.base import BaseCommand
from services.cosmos_db import CosmosDBService
from services.rag_search import RagSearchService


class Command(BaseCommand):
    help = 'Re-index all done links from Cosmos DB into Azure AI Search'

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=50)

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        total_indexed = 0
        total_failed = 0
        offset = 0

        self.stdout.write('Re-indexing done links into Azure AI Search...')

        while True:
            links = CosmosDBService.query('links', """
                SELECT * FROM c
                WHERE c.status = 'done'
                ORDER BY c.created_at DESC
                OFFSET @offset LIMIT @limit
            """, [
                {"name": "@offset", "value": offset},
                {"name": "@limit", "value": batch_size},
            ])

            if not links:
                break

            for link in links:
                try:
                    RagSearchService.index_link(link)
                    total_indexed += 1
                    self.stdout.write(f"  Indexed: {link.get('title', link['id'])}")
                except Exception as e:
                    total_failed += 1
                    self.stdout.write(self.style.ERROR(f"  Failed: {link['id']} — {e}"))

            offset += batch_size
            if len(links) < batch_size:
                break

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. Indexed: {total_indexed}, Failed: {total_failed}'
        ))
