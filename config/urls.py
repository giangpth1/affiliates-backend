from django.urls import path, include

urlpatterns = [
    path('admin/', include('apps.admin_dashboard.urls')),
    path('api/auth/', include('apps.users.urls')),
    path('api/links/', include('apps.links.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/search/', include('apps.search.urls')),
]
