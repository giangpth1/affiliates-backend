from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Disable JWT auth for local development convenience
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
    'apps.users.authentication.CosmosJWTAuthentication',
]
REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
    'rest_framework.permissions.AllowAny',
]
