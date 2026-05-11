from django.urls import path
from . import views

urlpatterns = [
    path('', views.LinkListView.as_view(), name='link-list'),
    path('<str:link_id>/', views.LinkDetailView.as_view(), name='link-detail'),
]
