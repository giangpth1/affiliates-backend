from dataclasses import dataclass
from typing import Optional
from apps.core.models import BaseDocument


@dataclass
class Product(BaseDocument):
    title: str = ""
    original_url: str = ""  # Resolved Shopee URL (https://shopee.vn/product/...)
    affiliate_url: str = ""  # User's original affiliate link (may be short link)
    randomized_url: str = ""  # URL with randomized params for scraping (anti-detection)
    shop_id: str = ""
    shop_name: str = ""  # Shop name extracted from Shopee
    item_id: str = ""
    thumbnail_url: str = ""
    thumbnail_original: str = ""
    price: Optional[float] = None
    price_currency: str = "VND"
    category: Optional[str] = None
    status: str = "active"
