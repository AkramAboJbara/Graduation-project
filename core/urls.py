from django.urls import path,include
from .views import HomepageProductAPIView, homepage
from rest_framework.authtoken.views import obtain_auth_token
from .views import viewsets_product,viewsets_category
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('product', viewsets_product)
router.register('category', viewsets_category)


urlpatterns = [
    path('', homepage, name='homepage'),
    path('home/products/', HomepageProductAPIView.as_view(), name='homepage-products'),
    path('category/', include(router.urls)),
    path('product/', include(router.urls)),
]
