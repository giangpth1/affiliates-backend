from rest_framework.exceptions import APIException
from rest_framework import status


class DocumentNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Document not found.'


class ScrapingFailed(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Failed to scrape product data.'


class InvalidShopeeURL(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid Shopee affiliate URL.'


class CosmosDBError(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Database service unavailable.'
