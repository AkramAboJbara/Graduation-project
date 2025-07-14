from datetime import timedelta
from django.http import JsonResponse
import django_filters
from rest_framework import status, filters, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django_filters import rest_framework as filters
import stripe
from django.utils import timezone
from .models import *
from .serializers import * 
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from rest_framework import filters
from rest_framework.decorators import action
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test


superuser_required = user_passes_test(
    lambda u: u.is_superuser,
    login_url='/admin/login/' 
)


authentication_classes = [TokenAuthentication] 

@superuser_required
def Admin_dashboard(request):
    return render(request , 'admin-dashboard.html')

class viewsets_product(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    lookup_field = 'slug'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = request.query_params.get('page', 1)  # get the page number from the request
        paginator = Paginator(queryset, 20)  # show 20 items per page

        try:
            paginated_products = paginator.page(page)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)  
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)  # if page is out of range, deliver last page

        serializer = self.get_serializer(paginated_products, many=True)

        return Response({
            'total_pages': paginator.num_pages,
            'current_page': paginated_products.number,
            'products': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='top-sales')
    def top_sales(self, request):
        top_products = Product.objects.order_by('-sales')[:5]
        serializer = self.get_serializer(top_products, many=True)
        return Response(serializer.data)


class viewsets_category(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name','description']
    lookup_field = 'slug'



class AddToCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))  # quantity should be an integer

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # validate stock
        if product.stock < quantity:
            return Response(
                {"error": f"Not enough stock available. Only {product.stock} items left."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            # check if the updated quantity exceeds the stock
            if product.stock < (cart_item.quantity + quantity):
                return Response(
                    {"error": f"Not enough stock available. Only {product.stock} items left."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        # decrease the product stock
        product.stock -= quantity
        product.save()

        # recalculate the cart total based on all items in the cart
        cart_items = CartItem.objects.filter(cart=cart)
        cart.total = sum(Decimal(str(item.product.price)) * Decimal(str(item.quantity)) for item in cart_items)
        cart.save()
        serializer = CartItemSerializer(cart_item)
        return Response(
            {
                "cart_item": serializer.data,
                "total_price": float(cart.total)  # convert decimal to float 
            },
            status=status.HTTP_201_CREATED
        )
    
    
class RemoveFromCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')
        quantity_to_remove = int(request.data.get('quantity', 1))  #quantity should be an integer

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        if not cart.items.exists():
            return Response({"error": "Cart is empty. No items to remove."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
        except CartItem.DoesNotExist:
            return Response({"error": "Product not found in the cart"}, status=status.HTTP_404_NOT_FOUND)

        if quantity_to_remove > cart_item.quantity: # validate the quantity to remove
            return Response(
                {"error": f"Cannot remove more than {cart_item.quantity} items."},
                status=status.HTTP_400_BAD_REQUEST
            )
        product.stock += quantity_to_remove # update the product stock
        product.save()
        if quantity_to_remove == cart_item.quantity:
            cart_item.delete() # remove the entire item from the cart
        else:
            cart_item.quantity -= quantity_to_remove
            cart_item.save()

        # recalculate the cart total based on all items in the cart
        cart_items = CartItem.objects.filter(cart=cart)
        cart.total = sum(Decimal(str(item.product.price)) * Decimal(str(item.quantity)) for item in cart_items)
        cart.save()

        return Response(
            {
                "message": "Product quantity updated in cart",
                "total_price": float(cart.total)  # convert decimal to float for response
            },
            status=status.HTTP_200_OK
        )
    

class ViewCartContentApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response(
                {"message": "No cart exists for this user."},
                status=status.HTTP_200_OK
            )
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        response_data = {
            "total_price": float(total_price),  
            "products": [
                {
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price": float(item.product.price * item.quantity),   #convert decimal to float
                    "image": item.product.image   
                }
                for item in cart_items
            ]
        }

        return Response(response_data, status=status.HTTP_200_OK)  
    
    
class HomepageAPIView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


# Stripe integration
stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response(
                {"message": "No cart exists for this user."},
                status=status.HTTP_200_OK
            )
        cart_items = CartItem.objects.filter(cart=cart)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items = [
                    {   
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(item.product.price * 100),  # Convert to cents
                            'product_data': {
                                'name': item.product.name,
                                "images": [item.product.image] if item.product.image else [],
                            },
                        },
                        'quantity': item.quantity,
                    }
                for item in cart_items
            ],
            mode='payment',
            customer_email=user.email,
            metadata={
                "cart_id": str(cart.id),
                "user_id": str(user.id)
            },
            success_url='https://hamza-masoud.github.io/e-commerce-frontend/',
            cancel_url='https://hamza-masoud.github.io/e-commerce-frontend//about',
        )
        return Response({
                "id": checkout_session
        })
        
#stripe listen --forward-to localhost:8000/api/Stripe_Webhook_APIView/
webhook_key = settings.STRIPE_WEBHOOK_KEY
class StripeWebhookAPIView(APIView):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        event = None
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_key
            )
        except ValueError:
            return Response({"error": "Invalid payload"}, status=400)
        except stripe.error.SignatureVerificationError:
            return Response({"error": "Invalid signature"}, status=400)
        if event["type"] == "checkout.session.completed":
        #update database , send email ,anything :)
            session = event["data"]["object"]
            cart_id = session.get("metadata", {}).get("cart_id")
            user_id = session.get("metadata", {}).get("user_id")
            cart = Cart.objects.get(id=cart_id)
            user = User.objects.get(id=user_id)
            cart_items = CartItem.objects.filter(cart=cart)
            
            # Send email
            context = {
                'user': user.first_name,
                'cart': cart,
                'cart_items': cart_items,
                'total': cart.total,
            }

            html_message = render_to_string('receipt.html', context)
            plain_message = strip_tags(html_message)

            send_mail(
                subject="Your Purchase Receipt",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message
            )
                        # Create the order
            order = Order.objects.create(
                user=user,
                full_name=user.get_full_name(),
                email=user.email,
                address=user.address,
                total_amount=cart.total,
                created_at=timezone.now(),
                status='Pending'
            )

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price * Decimal(item.quantity)
                )
                item.product.sales += item.quantity
                item.product.date_sold = timezone.now()
                item.product.save()

            cart_items.delete()
            cart.total = 0
            cart.save()
        return Response({"status": "success"}, status=200)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        user_data = UserSerializer(user).data
        orders = Order.objects.filter(user=user).order_by('-created_at')
        orders_data = OrderSerializer(orders, many=True).data
        return Response({
            'user': user_data,
            'orders': orders_data
        }, status=status.HTTP_200_OK)
        
    def patch(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        allowed_fields = [ 'phone_number', 'address']
        update_data = {field: data[field] for field in allowed_fields if field in data}
        serializer = UserSerializer(user, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'user': serializer.data, 'message': 'Profile updated successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, order_id, *args, **kwargs):
        user = request.user
        try:
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)


        if timezone.now() - order.created_at > timedelta(hours=2):
            return Response({'error': 'Orders can only be deleted within 2 hours of creation.'}, status=status.HTTP_403_FORBIDDEN)

    
        for item in order.items.all():  
            product = item.product
            product.stock += item.quantity 
            product.save()

        order.delete()
        return Response({'message': 'Order deleted and stock updated.'}, status=status.HTTP_200_OK)
@superuser_required
def manage_orders_view(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'orders/manage_orders.html', {'orders': orders})

@superuser_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order._meta.get_field('status').choices):
            order.status = new_status
            order.save()
        return redirect('manage_orders')
    status_choices = Order._meta.get_field('status').choices
    return render(request, 'orders/update_order_status.html', {'order': order, 'status_choices': status_choices})
