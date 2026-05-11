import bcrypt
import uuid
from datetime import datetime
from typing import Optional
from services.cosmos_db import CosmosDBService
from apps.users.models import User
from rest_framework.exceptions import ValidationError, AuthenticationFailed


class UserService:
    CONTAINER = 'users'

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    @staticmethod
    def exists_by_email(email: str) -> bool:
        query = "SELECT c.id FROM c WHERE c.email = @email"
        params = [{"name": "@email", "value": email.lower()}]
        items = CosmosDBService.query(UserService.CONTAINER, query, params)
        return len(items) > 0

    @staticmethod
    def create(email: str, password: str, display_name: str) -> User:
        email = email.lower().strip()

        if UserService.exists_by_email(email):
            raise ValidationError({"email": "Email đã được đăng ký."})

        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=UserService.hash_password(password),
            display_name=display_name.strip(),
            status='active',
            email_verified=False,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        CosmosDBService.upsert(UserService.CONTAINER, user.to_dict())
        return user

    @staticmethod
    def _clean_doc(doc: dict) -> dict:
        return {k: v for k, v in doc.items() if not k.startswith('_')}

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        query = "SELECT * FROM c WHERE c.email = @email"
        params = [{"name": "@email", "value": email.lower()}]
        items = CosmosDBService.query(UserService.CONTAINER, query, params)
        return User(**UserService._clean_doc(items[0])) if items else None

    @staticmethod
    def get_by_id(user_id: str) -> User:
        query = "SELECT * FROM c WHERE c.id = @id"
        params = [{"name": "@id", "value": user_id}]
        items = CosmosDBService.query(UserService.CONTAINER, query, params)
        if not items:
            from apps.core.exceptions import DocumentNotFound
            raise DocumentNotFound(detail=f"User {user_id} not found.")
        return User(**UserService._clean_doc(items[0]))

    @staticmethod
    def authenticate(email: str, password: str) -> User:
        user = UserService.get_by_email(email)

        if not user or not UserService.verify_password(password, user.password_hash):
            raise AuthenticationFailed("Email hoặc mật khẩu không đúng.")

        if user.status != 'active':
            raise AuthenticationFailed("Tài khoản đã bị tạm khóa.")

        user.last_login_at = datetime.utcnow().isoformat()
        user.login_count += 1
        user.updated_at = datetime.utcnow().isoformat()
        CosmosDBService.upsert(UserService.CONTAINER, user.to_dict())

        return user

    @staticmethod
    def change_password(user_id: str, old_password: str, new_password: str) -> None:
        user = UserService.get_by_id(user_id)

        if not UserService.verify_password(old_password, user.password_hash):
            raise AuthenticationFailed("Mật khẩu hiện tại không đúng.")

        user.password_hash = UserService.hash_password(new_password)
        user.updated_at = datetime.utcnow().isoformat()
        CosmosDBService.upsert(UserService.CONTAINER, user.to_dict())
