from django.urls import path
from .views import CategoryListAPIView, HomepageProductAPIView, homepage, AddToCartView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', homepage, name='homepage'),
    path('home/products/', HomepageProductAPIView.as_view(), name='homepage-products'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
]
