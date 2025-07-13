from django.urls import path
from .views import  SignupView, LoginView ,LogoutView
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
    PasswordResetRequestView,
    CodeVerificationView,
)

urlpatterns = [
    path('api/signup/', SignupView.as_view(), name='signup'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/api-token-auth', obtain_auth_token),
    path('password_reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('verify_code/', CodeVerificationView.as_view(), name='verify_code'),
    path('password_reset_done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
]