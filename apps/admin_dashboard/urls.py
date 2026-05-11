from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('login/', views.AdminLoginView.as_view(), name='login'),
    path('logout/', views.AdminLogoutView.as_view(), name='logout'),

    path('', views.DashboardView.as_view(), name='dashboard'),

    path('users/', views.UserListView.as_view(), name='users'),
    path('users/<str:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<str:user_id>/delete/', views.UserDeleteView.as_view(), name='user_delete'),

    path('products/', views.ProductListView.as_view(), name='products'),
    path('products/<str:shop_id>/<str:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<str:shop_id>/<str:product_id>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    path('links/', views.LinkListView.as_view(), name='links'),
    path('links/<str:user_id>/<str:link_id>/', views.LinkDetailView.as_view(), name='link_detail'),
    path('links/<str:user_id>/<str:link_id>/retry/', views.LinkRetryView.as_view(), name='link_retry'),
    path('links/<str:user_id>/<str:link_id>/delete/', views.LinkDeleteView.as_view(), name='link_delete'),
]
