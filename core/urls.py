from django.urls import path,include
from .views import *
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('product', viewsets_product)
router.register('category', viewsets_category)


urlpatterns = [
    path('homepage/', HomepageAPIView.as_view(), name='homepage'),
    path('category/', include(router.urls)),
    path('product/', include(router.urls)),
    path('add_to_cart/', AddToCartAPIView.as_view(), name='add-to-cart'),
    path('remove_from_cart/', RemoveFromCartAPIView.as_view(), name='remove-from-cart'),
    path('view_cart/', ViewCartContentApiView.as_view(), name='view_cart'),
    path('create_checkout_session/', CreateCheckoutSessionAPIView.as_view(), name='create_checkout_session'),
    path('Stripe_Webhook_APIView/', StripeWebhookAPIView.as_view(), name='Stripe_Webhook_APIView'),
    path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('admin/manage-orders/', manage_orders_view, name='manage_orders'),
    path('admin/manage-orders/<int:order_id>/update/', update_order_status, name='update_order_status'),
    path('admin-dashboard' , Admin_dashboard , name='admin-dashboard')
]
