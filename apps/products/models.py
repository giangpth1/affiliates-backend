from dataclasses import dataclass
from typing import Optional
from apps.core.models import BaseDocument


@dataclass
class Product(BaseDocument):
    title: str = ""
    original_url: str = ""
    affiliate_url: str = ""
    randomized_url: str = ""
    shop_id: str = ""
    shop_name: str = ""
    item_id: str = ""
    thumbnail_url: str = ""
    thumbnail_original: str = ""
    price: Optional[float] = None
    price_currency: str = "VND"
    category: Optional[str] = None
    status: str = "active"
    user_id: str = ""
