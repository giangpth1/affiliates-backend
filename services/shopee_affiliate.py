import hashlib
import hmac
import time
import logging
import httpx

logger = logging.getLogger(__name__)

GRAPHQL_URL = "https://open-api.affiliate.shopee.vn/graphql"


class ShopeeAffiliateService:

    def __init__(self, app_id: str, secret: str):
        self.app_id = app_id
        self.secret = secret

    def _auth_headers(self) -> dict:
        timestamp = str(int(time.time()))
        payload = f"{self.app_id}{timestamp}"
        signature = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return {
            "Authorization": f"SHA256 Credential={self.app_id}, Timestamp={timestamp}, Signature={signature}",
            "Content-Type": "application/json",
        }

    def _query(self, query: str, variables: dict) -> dict:
        headers = self._auth_headers()
        with httpx.Client(timeout=15) as client:
            response = client.post(
                GRAPHQL_URL,
                json={"query": query, "variables": variables},
                headers=headers,
            )
        logger.info(f"[AFFILIATE] HTTP {response.status_code}")
        response.raise_for_status()
        return response.json()

    def get_product(self, shop_id: str, item_id: str) -> dict:
        query = """
        query getProduct($shopId: Int!, $itemId: Int!) {
          productOfferV2(shopId: $shopId, itemId: $itemId) {
            itemId
            shopId
            productName
            imageUrl
            priceMin
            priceMax
            productLink
            shopName
            commissionRate
            sales
            ratingStar
            offerLink
            periodStartTime
            periodEndTime
          }
        }
        """
        variables = {"shopId": int(shop_id), "itemId": int(item_id)}
        return self._query(query, variables)

    def generate_affiliate_link(self, original_url: str, sub_id: str) -> dict:
        query = """
        mutation generateLink($input: GenerateAffiliateLinkInput!) {
          generateAffiliateLink(input: $input) {
            shortLink
            longLink
          }
        }
        """
        variables = {
            "input": {
                "originalUrl": original_url,
                "subIds": [sub_id],
            }
        }
        return self._query(query, variables)

    @staticmethod
    def debug_product(shop_id: str, item_id: str) -> None:
        """Test: call API and log everything returned."""
        import json
        from django.conf import settings

        app_id = getattr(settings, "SHOPEE_APP_ID", "")
        secret = getattr(settings, "SHOPEE_SECRET", "")

        if not app_id or not secret:
            logger.warning("[AFFILIATE] SHOPEE_APP_ID / SHOPEE_SECRET chưa được set trong .env")
            return

        svc = ShopeeAffiliateService(app_id, secret)

        logger.info(f"[AFFILIATE] get_product shop_id={shop_id} item_id={item_id}")
        try:
            result = svc.get_product(shop_id, item_id)
            logger.info(f"[AFFILIATE] Raw response: {json.dumps(result, ensure_ascii=False)[:1000]}")

            errors = result.get("errors")
            if errors:
                logger.warning(f"[AFFILIATE] GraphQL errors: {errors}")
                return

            data = result.get("data", {}).get("productOfferV2", {})
            if not data:
                logger.warning("[AFFILIATE] productOfferV2 trống — field name có thể sai")
                return

            logger.info(f"[AFFILIATE] productName : {data.get('productName')}")
            logger.info(f"[AFFILIATE] shopName    : {data.get('shopName')}")
            logger.info(f"[AFFILIATE] priceMin    : {data.get('priceMin')}")
            logger.info(f"[AFFILIATE] priceMax    : {data.get('priceMax')}")
            logger.info(f"[AFFILIATE] imageUrl    : {data.get('imageUrl')}")
            logger.info(f"[AFFILIATE] commissionRate: {data.get('commissionRate')}")
            logger.info(f"[AFFILIATE] offerLink   : {data.get('offerLink')}")

        except httpx.HTTPStatusError as e:
            logger.error(f"[AFFILIATE] HTTP error: {e.response.status_code} — {e.response.text[:300]}")
        except Exception as e:
            logger.error(f"[AFFILIATE] Error: {e}", exc_info=True)
