from dataclasses import dataclass
from typing import Optional
from apps.core.models import BaseDocument


@dataclass
class AffLink(BaseDocument):
    original_url: str = ""
    resolved_url: str = ""
    shop_id: str = ""
    item_id: str = ""
    product_id: Optional[str] = None
    user_id: str = "default"
    status: str = "pending"
    error_message: Optional[str] = None
    notes: Optional[str] = None
