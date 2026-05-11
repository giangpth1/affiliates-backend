from rest_framework.views import APIView
from rest_framework.response import Response
from apps.links.services import LinkService
from apps.links.serializers import AffLinkSerializer


class ProductListView(APIView):
    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        user_id = request.user.id
        items, total = LinkService.list_done_for_user(user_id, page, page_size)
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': AffLinkSerializer(items, many=True).data,
        })
