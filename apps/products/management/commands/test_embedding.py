from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Test Azure OpenAI embedding configuration'

    def handle(self, *args, **options):
        self.stdout.write('Azure OpenAI config:')
        self.stdout.write(f'  Endpoint : {settings.AZURE_OPENAI_ENDPOINT}')
        self.stdout.write(f'  Deployment: {settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}')
        self.stdout.write(f'  API version: {settings.AZURE_OPENAI_API_VERSION}')
        self.stdout.write(f'  API key: {settings.AZURE_OPENAI_API_KEY[:10]}...')
        self.stdout.write('')

        try:
            from langchain_openai import AzureOpenAIEmbeddings
            embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                azure_deployment=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                api_version=settings.AZURE_OPENAI_API_VERSION,
            )
            self.stdout.write('Calling embed_query("sữa tắm")...')
            vector = embeddings.embed_query('sữa tắm')
            self.stdout.write(self.style.SUCCESS(
                f'OK — vector length: {len(vector)}, first 3 values: {vector[:3]}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'FAILED: {e}'))
