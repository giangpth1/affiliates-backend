from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.links.services import LinkService
from apps.links.serializers import AffLinkSerializer, CreateLinkSerializer


class LinkListView(APIView):
    def get(self, request):
        user_id = request.user.id
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        items, total = LinkService.list_for_user(user_id, page, page_size)
        serializer = AffLinkSerializer(items, many=True)
        return Response({'count': total, 'results': serializer.data})

    def post(self, request):
        serializer = CreateLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        url = serializer.validated_data['url']
        user_id = serializer.validated_data.get('user_id', 'default')

        link = LinkService.create_and_process(url, user_id)

        return Response(AffLinkSerializer(link).data, status=status.HTTP_201_CREATED)


class LinkDetailView(APIView):
    def get(self, request, link_id):
        user_id = request.user.id
        link = LinkService.get(link_id, user_id)
        return Response(AffLinkSerializer(link).data)
