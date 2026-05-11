from rest_framework import serializers


class ProductSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField()
    original_url = serializers.URLField()
    shop_id = serializers.CharField(read_only=True)
    item_id = serializers.CharField(read_only=True)
    thumbnail_url = serializers.URLField(read_only=True)
    price = serializers.FloatField(allow_null=True, required=False)
    price_currency = serializers.CharField(default='VND')
    category = serializers.CharField(allow_null=True, required=False)
    status = serializers.CharField(read_only=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class ProductListSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    original_url = serializers.URLField()
    affiliate_url = serializers.URLField(required=False, allow_blank=True)
    randomized_url = serializers.URLField(required=False, allow_blank=True)
    shop_id = serializers.CharField()
    shop_name = serializers.CharField(required=False, allow_blank=True)
    item_id = serializers.CharField(required=False)
    thumbnail_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    price = serializers.FloatField(allow_null=True, required=False)
    price_currency = serializers.CharField(default='VND', required=False)
    status = serializers.CharField(default='active', required=False)
    created_at = serializers.CharField()
