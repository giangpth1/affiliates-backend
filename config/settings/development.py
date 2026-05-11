from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Disable JWT auth for local development convenience
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
    'apps.users.authentication.CosmosJWTAuthentication',
]
REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
    'rest_framework.permissions.AllowAny',
]
