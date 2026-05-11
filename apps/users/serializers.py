from rest_framework import serializers
import re
from apps.users.services import UserService


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    display_name = serializers.CharField(min_length=2, max_length=50)

    def validate_email(self, value):
        value = value.lower().strip()
        if UserService.exists_by_email(value):
            raise serializers.ValidationError("Email này đã được đăng ký.")
        return value

    def validate_password(self, value):
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất 1 chữ hoa.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất 1 chữ thường.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất 1 số.")
        return value

    def validate_display_name(self, value):
        value = value.strip()
        if not re.match(r'^[a-zA-ZÀ-ỹ\s\.]+$', value):
            raise serializers.ValidationError("Tên chỉ được chứa chữ cái và khoảng trắng.")
        return value


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.Serializer):
    id = serializers.CharField()
    email = serializers.EmailField()
    display_name = serializers.CharField()
    status = serializers.CharField()
    email_verified = serializers.BooleanField()
    avatar_url = serializers.CharField(allow_null=True)
    created_at = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
