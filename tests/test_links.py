from unittest.mock import patch
from django.test import TestCase, RequestFactory
from apps.links.views import LinkListView
import json


class TestLinkCreation(TestCase):

    @patch('apps.links.services.ShopeeScraperService.validate_url', return_value=True)
    @patch('apps.links.services.CosmosDBService.upsert')
    @patch('apps.links.services.LinkService._trigger_scraping')
    def test_create_link_returns_201(self, mock_trigger, mock_upsert, mock_validate):
        mock_upsert.return_value = {
            'id': 'test-id', 'original_url': 'https://shp.ee/test',
            'status': 'pending', 'user_id': 'default',
            'created_at': '2026-05-06', 'updated_at': '2026-05-06'
        }
        factory = RequestFactory()
        req = factory.post(
            '/api/links/',
            data=json.dumps({'url': 'https://shp.ee/test'}),
            content_type='application/json'
        )
        response = LinkListView.as_view()(req)
        self.assertEqual(response.status_code, 201)
