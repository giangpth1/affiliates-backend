from dataclasses import dataclass
from typing import Optional
from apps.core.models import BaseDocument


@dataclass
class AffLink(BaseDocument):
    original_url: str = ""
    user_id: str = "default"
    status: str = "pending"
    error_message: Optional[str] = None
    notes: Optional[str] = None
    # Product data — populated after processing
    title: str = ""
    shop_id: str = ""
    shop_name: str = ""
    item_id: str = ""
    thumbnail_url: str = ""
    price: Optional[float] = None
    resolved_url: str = ""
