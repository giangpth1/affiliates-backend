import logging
import unicodedata
from django.conf import settings
from langchain_openai import AzureOpenAIEmbeddings
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential

logger = logging.getLogger(__name__)

VECTOR_DIMENSIONS = 1536  # text-embedding-3-small


def _normalize_text(text: str) -> str:
    """Remove Vietnamese diacritics and lowercase — 'sữa tắm' → 'sua tam'."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower().strip()


_embeddings = None
_search_client = None
_index_ready = False


def _get_embeddings() -> AzureOpenAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            azure_deployment=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )
    return _embeddings


def _get_search_client() -> SearchClient:
    global _search_client
    if _search_client is None:
        _search_client = SearchClient(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            index_name=settings.AZURE_SEARCH_INDEX,
            credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY),
        )
    return _search_client


def _ensure_index() -> None:
    global _index_ready
    if _index_ready:
        return

    index_client = SearchIndexClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY),
    )

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="title_normalized", type=SearchFieldDataType.String),
        SimpleField(name="thumbnail_url", type=SearchFieldDataType.String),
        SimpleField(name="original_url", type=SearchFieldDataType.String),
        SimpleField(name="user_id", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="shop_name", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="price", type=SearchFieldDataType.Double, filterable=True, sortable=True),
        SimpleField(name="created_at", type=SearchFieldDataType.String, sortable=True),
        SearchField(
            name="title_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=VECTOR_DIMENSIONS,
            vector_search_profile_name="hnsw-profile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw-algo")],
        profiles=[VectorSearchProfile(name="hnsw-profile", algorithm_configuration_name="hnsw-algo")],
    )

    index = SearchIndex(
        name=settings.AZURE_SEARCH_INDEX,
        fields=fields,
        vector_search=vector_search,
    )

    try:
        index_client.create_or_update_index(index)
        logger.info(f"Azure Search index '{settings.AZURE_SEARCH_INDEX}' ensured with vector field")
        _index_ready = True
    except Exception as e:
        if 'cannot be updated' in str(e).lower():
            logger.warning("Index schema conflict detected, deleting and recreating index...")
            try:
                index_client.delete_index(settings.AZURE_SEARCH_INDEX)
                index_client.create_or_update_index(index)
                logger.info(f"Azure Search index '{settings.AZURE_SEARCH_INDEX}' recreated successfully")
                _index_ready = True
            except Exception as e2:
                logger.error(f"Failed to recreate search index: {e2}", exc_info=True)
        else:
            logger.error(f"Failed to ensure search index: {e}", exc_info=True)


class RagSearchService:

    @staticmethod
    def index_link(link: dict) -> None:
        title = link.get('title', '').strip()
        if not title:
            return
        try:
            _ensure_index()
            vector = _get_embeddings().embed_query(title)
            raw_price = link.get('price')
            document = {
                'id': link['id'],
                'title': title,
                'title_normalized': _normalize_text(title),
                'title_vector': vector,
                'user_id': link.get('user_id', ''),
                'thumbnail_url': link.get('thumbnail_url', ''),
                'original_url': link.get('original_url', ''),
                'shop_name': link.get('shop_name', ''),
                'price': float(raw_price) if raw_price is not None else None,
                'created_at': link.get('created_at', ''),
            }
            result = _get_search_client().merge_or_upload_documents(documents=[document])
            if result[0].succeeded:
                logger.info(f"RAG indexed link {link['id']}: '{title}'")
            else:
                logger.error(f"RAG index failed for link {link['id']}: {result[0].errors}")
        except Exception as e:
            logger.error(f"RAG index_link error for {link.get('id')}: {e}", exc_info=True)

    @staticmethod
    def search(query: str, user_id: str = None, top: int = 10, min_price: float = None, max_price: float = None) -> list[dict]:
        try:
            _ensure_index()
            query_vector = _get_embeddings().embed_query(query)

            vector_query = VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=top,
                fields="title_vector",
            )

            filters = []
            if user_id:
                filters.append(f"user_id eq '{user_id}'")
            if min_price is not None:
                filters.append(f"price ge {min_price}")
            if max_price is not None:
                filters.append(f"price le {max_price}")
            filter_str = " and ".join(filters) if filters else None

            results = _get_search_client().search(
                search_text=_normalize_text(query),
                vector_queries=[vector_query],
                filter=filter_str,
                top=top,
                select=["id", "title", "thumbnail_url", "original_url", "price", "shop_name", "created_at"],
            )

            MIN_SCORE = 0.02
            return [
                {**dict(r), 'score': r['@search.score'], 'highlights': {}}
                for r in results
                if r['@search.score'] >= MIN_SCORE
            ]

        except Exception as e:
            logger.error(f"RAG search error: {e}", exc_info=True)
            return []

    @staticmethod
    def delete_link(link_id: str) -> None:
        try:
            _get_search_client().delete_documents(documents=[{'id': link_id}])
        except Exception as e:
            logger.error(f"RAG delete error for link {link_id}: {e}", exc_info=True)
