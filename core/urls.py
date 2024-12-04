from django.urls import path
from .views import CategoryListAPIView, HomepageProductAPIView, SignupView, LoginView, homepage
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('', homepage, name='homepage'),
    path('home/products/', HomepageProductAPIView.as_view(), name='homepage-products'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('api-token-auth', obtain_auth_token),

]
