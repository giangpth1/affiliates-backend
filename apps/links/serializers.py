from rest_framework import serializers


class CreateLinkSerializer(serializers.Serializer):
    url = serializers.URLField()
    user_id = serializers.CharField(default='default', required=False)
    notes = serializers.CharField(allow_blank=True, required=False)


class AffLinkSerializer(serializers.Serializer):
    id = serializers.CharField()
    original_url = serializers.URLField()
    resolved_url = serializers.URLField(allow_blank=True, required=False)
    product_id = serializers.CharField(allow_null=True, required=False)
    status = serializers.CharField()
    notes = serializers.CharField(allow_null=True, required=False)
    error_message = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.CharField()
    updated_at = serializers.CharField()
