from rest_framework import serializers


class CreateLinkSerializer(serializers.Serializer):
    url = serializers.URLField()
    user_id = serializers.CharField(default='default', required=False)
    notes = serializers.CharField(allow_blank=True, required=False)


class AffLinkSerializer(serializers.Serializer):
    id = serializers.CharField()
    original_url = serializers.URLField()
    status = serializers.CharField()
    notes = serializers.CharField(allow_null=True, required=False)
    error_message = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.CharField()
    updated_at = serializers.CharField()
    title = serializers.CharField(allow_blank=True, required=False)
    shop_id = serializers.CharField(allow_blank=True, required=False)
    shop_name = serializers.CharField(allow_blank=True, required=False)
    item_id = serializers.CharField(allow_blank=True, required=False)
    thumbnail_url = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    price = serializers.FloatField(allow_null=True, required=False)
    resolved_url = serializers.CharField(allow_blank=True, required=False)
