from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.products.services import ProductService
from apps.products.serializers import ProductSerializer, ProductListSerializer


class ProductListView(APIView):
    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        items, total = ProductService.list_all(page, page_size)
        serializer = ProductListSerializer(items, many=True)
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': serializer.data,
        })


class ProductDetailView(APIView):
    def get(self, request, product_id):
        shop_id = request.query_params.get('shop_id', '')
        product = ProductService.get(product_id, shop_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def delete(self, request, product_id):
        shop_id = request.query_params.get('shop_id', '')
        ProductService.delete(product_id, shop_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
