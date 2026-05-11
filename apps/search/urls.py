from django.urls import path
from .views import SmartSearchView

urlpatterns = [
    path('', SmartSearchView.as_view(), name='smart-search'),
]
