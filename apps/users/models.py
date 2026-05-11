from dataclasses import dataclass
from typing import Optional
from apps.core.models import BaseDocument


@dataclass
class User(BaseDocument):
    email: str
    password_hash: str
    display_name: str

    status: str = "active"
    role: str = "user"
    email_verified: bool = False

    phone: Optional[str] = None
    avatar_url: Optional[str] = None

    last_login_at: Optional[str] = None
    login_count: int = 0

    @property
    def is_authenticated(self) -> bool:
        """Always return True for authenticated users (required by DRF)"""
        return True

    @property
    def is_active(self) -> bool:
        """Check if user account is active"""
        return self.status == 'active'

    @property
    def is_anonymous(self) -> bool:
        """Always return False (required by DRF)"""
        return False

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def to_response(self) -> dict:
        return {
            'id': self.id,
            'email': self.email,
            'display_name': self.display_name,
            'status': self.status,
            'email_verified': self.email_verified,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at,
        }
