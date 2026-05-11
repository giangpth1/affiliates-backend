from services.cosmos_db import CosmosDBService
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class AdminService:

    @staticmethod
    def get_dashboard_stats() -> dict:
        cosmos = CosmosDBService

        users_result = cosmos.query('users', "SELECT VALUE COUNT(1) FROM c")
        total_users = users_result[0] if users_result else 0

        products_result = cosmos.query('products', "SELECT VALUE COUNT(1) FROM c")
        total_products = products_result[0] if products_result else 0

        links_pending = cosmos.query('links', "SELECT VALUE COUNT(1) FROM c WHERE c.status = 'pending'")
        links_processing = cosmos.query('links', "SELECT VALUE COUNT(1) FROM c WHERE c.status = 'processing'")
        links_done = cosmos.query('links', "SELECT VALUE COUNT(1) FROM c WHERE c.status = 'done'")
        links_failed = cosmos.query('links', "SELECT VALUE COUNT(1) FROM c WHERE c.status = 'failed'")

        return {
            'total_users': total_users,
            'total_products': total_products,
            'links': {
                'pending': links_pending[0] if links_pending else 0,
                'processing': links_processing[0] if links_processing else 0,
                'done': links_done[0] if links_done else 0,
                'failed': links_failed[0] if links_failed else 0,
            }
        }

    @staticmethod
    def list_users(page: int = 1, page_size: int = 20) -> tuple[list, int]:
        cosmos = CosmosDBService
        offset = (page - 1) * page_size

        count_result = cosmos.query('users', "SELECT VALUE COUNT(1) FROM c")
        total = count_result[0] if count_result else 0

        query = f"SELECT * FROM c ORDER BY c.created_at DESC OFFSET {offset} LIMIT {page_size}"
        users = cosmos.query('users', query)

        for user in users:
            user.pop('password_hash', None)

        return users, total

    @staticmethod
    def get_user(user_id: str) -> dict | None:
        cosmos = CosmosDBService
        try:
            user = cosmos.get_by_id('users', user_id, user_id)
            user.pop('password_hash', None)
            return user
        except Exception:
            return None

    @staticmethod
    def update_user_status(user_id: str, status: str) -> dict | None:
        cosmos = CosmosDBService
        try:
            user = cosmos.get_by_id('users', user_id, user_id)
            user['status'] = status
            user['updated_at'] = datetime.now(timezone.utc).isoformat()
            cosmos.upsert('users', user)
            user.pop('password_hash', None)
            return user
        except Exception:
            return None

    @staticmethod
    def delete_user(user_id: str) -> bool:
        cosmos = CosmosDBService
        try:
            links = cosmos.query('links', f"SELECT c.id FROM c WHERE c.user_id = '{user_id}'")
            for link in links:
                try:
                    cosmos.delete('links', link['id'], user_id)
                except Exception:
                    pass

            cosmos.delete('users', user_id, user_id)
            return True
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            return False

    @staticmethod
    def list_products(page: int = 1, page_size: int = 20, shop_id: str = None) -> tuple[list, int]:
        cosmos = CosmosDBService
        offset = (page - 1) * page_size

        where_clause = f"WHERE c.shop_id = '{shop_id}'" if shop_id else ""
        count_query = f"SELECT VALUE COUNT(1) FROM c {where_clause}"
        count_result = cosmos.query('products', count_query)
        total = count_result[0] if count_result else 0

        query = f"SELECT * FROM c {where_clause} ORDER BY c.created_at DESC OFFSET {offset} LIMIT {page_size}"
        products = cosmos.query('products', query)

        return products, total

    @staticmethod
    def get_product(product_id: str, shop_id: str) -> dict | None:
        cosmos = CosmosDBService
        try:
            return cosmos.get_by_id('products', product_id, shop_id)
        except Exception:
            return None

    @staticmethod
    def delete_product(product_id: str, shop_id: str) -> bool:
        cosmos = CosmosDBService
        try:
            cosmos.delete('products', product_id, shop_id)
            try:
                from services.azure_search import AzureSearchService
                AzureSearchService.delete_product(product_id)
            except Exception:
                pass
            return True
        except Exception as e:
            logger.error(f"Failed to delete product {product_id}: {e}")
            return False

    @staticmethod
    def list_links(page: int = 1, page_size: int = 20, status: str = None) -> tuple[list, int]:
        cosmos = CosmosDBService
        offset = (page - 1) * page_size

        where_clause = f"WHERE c.status = '{status}'" if status else ""
        count_query = f"SELECT VALUE COUNT(1) FROM c {where_clause}"
        count_result = cosmos.query('links', count_query)
        total = count_result[0] if count_result else 0

        query = f"SELECT * FROM c {where_clause} ORDER BY c.created_at DESC OFFSET {offset} LIMIT {page_size}"
        links = cosmos.query('links', query)

        return links, total

    @staticmethod
    def get_link(link_id: str, user_id: str) -> dict | None:
        cosmos = CosmosDBService
        try:
            return cosmos.get_by_id('links', link_id, user_id)
        except Exception:
            return None

    @staticmethod
    def retry_failed_link(link_id: str, user_id: str) -> dict | None:
        cosmos = CosmosDBService
        try:
            link = cosmos.get_by_id('links', link_id, user_id)
            if link['status'] != 'failed':
                return None

            link['status'] = 'pending'
            link['error_message'] = None
            link['updated_at'] = datetime.now(timezone.utc).isoformat()
            cosmos.upsert('links', link)

            from apps.links.services import LinkService
            LinkService._trigger_scraping(link_id, link['original_url'])

            return link
        except Exception as e:
            logger.error(f"Failed to retry link {link_id}: {e}")
            return None

    @staticmethod
    def delete_link(link_id: str, user_id: str) -> bool:
        cosmos = CosmosDBService
        try:
            cosmos.delete('links', link_id, user_id)
            return True
        except Exception as e:
            logger.error(f"Failed to delete link {link_id}: {e}")
            return False
