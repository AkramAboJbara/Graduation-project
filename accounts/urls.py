from django.urls import path
from .views import  SignupView, LoginView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('api-token-auth', obtain_auth_token),

]