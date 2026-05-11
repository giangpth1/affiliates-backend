from rest_framework import serializers


class SearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(min_length=1, max_length=200)
    top = serializers.IntegerField(min_value=1, max_value=50, default=10, required=False)
    min_price = serializers.FloatField(required=False, allow_null=True)
    max_price = serializers.FloatField(required=False, allow_null=True)


class SearchResultSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    thumbnail_url = serializers.CharField(allow_blank=True, required=False)
    original_url = serializers.CharField(allow_blank=True, required=False)
    shop_name = serializers.CharField(allow_blank=True, required=False)
    price = serializers.FloatField(allow_null=True, required=False)
    created_at = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    score = serializers.FloatField()
    highlights = serializers.DictField(required=False)
