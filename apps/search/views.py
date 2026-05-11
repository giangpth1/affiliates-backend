from rest_framework.views import APIView
from rest_framework.response import Response
from services.azure_search import AzureSearchService
from apps.search.serializers import SearchQuerySerializer, SearchResultSerializer


class SmartSearchView(APIView):

    def get(self, request):
        serializer = SearchQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        results = AzureSearchService.semantic_search(
            query=serializer.validated_data['q'],
            top=serializer.validated_data.get('top', 10),
            min_price=serializer.validated_data.get('min_price'),
            max_price=serializer.validated_data.get('max_price'),
        )

        return Response({
            'query': serializer.validated_data['q'],
            'count': len(results),
            'results': SearchResultSerializer(results, many=True).data
        })
