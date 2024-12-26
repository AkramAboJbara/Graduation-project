from django.urls import path,include
from .views import CategoryListAPIView, HomepageProductAPIView, homepage
from rest_framework.authtoken.views import obtain_auth_token
from .views import viewsets_product
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('product', viewsets_product)


urlpatterns = [
    path('', homepage, name='homepage'),
    path('home/products/', HomepageProductAPIView.as_view(), name='homepage-products'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('product/', include(router.urls)),
]
